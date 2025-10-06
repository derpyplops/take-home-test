#!/usr/bin/env python3
"""
Log Classification Script using GPT-5

This script classifies call transcript logs using the same system prompt
as the Go voiceclassifier to determine user intent and generates a summary.
"""

import json
import os
import argparse
import csv
from datetime import datetime
from collections import Counter
from typing import Dict, List, Optional
import openai


# System prompt from voiceclassifier.go
CLASSIFY_SYSTEM_PROMPT = """
You are an responsible for classifying incoming call transcripts into relevant intent types so that the humans that are assigned to follow up know what is the best course of action.
You will be given a call transcript.
Focus exclusively on the user's reply, i.e. sentences that starts with 'User: '.
Read the transcripts carefully and classify the call transcript into the following categories:
- 'voice_interested': The User EXPLICITLY indicated he/she is interested in the course or the university.
- 'voice_not_interested': The user EXPLICITLY say that he/she is not interested in the course or the university.
- 'voice_immediate_hangup': The user hangs up without expressing their full intent. This includes cutting off halfway through when the caller is talking, or no substantial discussion after exchanging greetings.
- 'voice_wrong_number': The user who answered the phone indicated that we are calling the wrong number.
- 'voice_no_action': The student has already signed up to the course or is in contact with the advisor. Only use this if the student does not need any additional help.
- 'voice_wants_call_back': The user EXPLICITLY request that he/she wants a call back.
- 'voice_wants_email_follow_up': The user wished to follow up through email.
- 'voice_wants_whatsapp_sms_follow_up': The user wished to follow up through instant messaging, such as via Whatsapp or SMS.
- 'voice_voice_mail': The call goes into an automated reply or a voice mail. Reply does not come from an actual user.
- 'voice_unknown': Anything that does not fit into the above categories.
"""

CLASSIFY_USER_PROMPT = """
Transcript:
--- BEGIN TRANSCRIPT ---
{}
--- END TRANSCRIPT ---

Remember to focus on the User's replies to derive their intent, and not the Agent's!
Reply in the following JSON format {{'intent': <category>}}
"""


def classify_transcript(client: openai.OpenAI, transcript: str) -> str:
    """Classify a single transcript using GPT-5."""
    try:
        response = client.chat.completions.create(
            model="gpt-5-mini-2025-08-07",
            messages=[
                {
                    "role": "system",
                    "content": CLASSIFY_SYSTEM_PROMPT
                },
                {
                    "role": "user", 
                    "content": CLASSIFY_USER_PROMPT.format(transcript)
                }
            ],
            response_format={"type": "json_object"},
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("intent", "voice_unknown")
    
    except Exception as e:
        print(f"Error classifying transcript: {e}")
        return "voice_unknown"


def read_log_file(file_path: str) -> List[str]:
    """Read and parse log file. Supports CSV, JSON lines, and plain text."""
    transcripts = []
    
    # Check if it's a CSV file
    if file_path.lower().endswith('.csv'):
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Look for transcript column
                transcript = row.get('transcript', '')
                if transcript:
                    transcripts.append(transcript)
        return transcripts
    
    # Handle other formats (JSON lines, plain text)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        
        # Try to parse as JSON lines first
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            try:
                # Try parsing as JSON
                data = json.loads(line)
                if 'transcript' in data:
                    transcripts.append(data['transcript'])
                elif 'message' in data:
                    transcripts.append(data['message'])
                else:
                    # Use the whole JSON as text
                    transcripts.append(str(data))
            except json.JSONDecodeError:
                # Treat as plain text transcript
                transcripts.append(line)
    
    return transcripts


def generate_summary(classifications: Dict[str, int], total_count: int) -> str:
    """Generate a summary of classification results."""
    summary_lines = [
        f"Classification Summary ({total_count} transcripts processed)",
        "=" * 60,
        ""
    ]
    
    # Sort by count descending
    sorted_intents = sorted(classifications.items(), key=lambda x: x[1], reverse=True)
    
    for intent, count in sorted_intents:
        percentage = (count / total_count) * 100
        summary_lines.append(f"{intent:30} {count:4d} ({percentage:5.1f}%)")
    
    summary_lines.extend([
        "",
        "Intent Categories:",
        "- voice_interested: User interested in course/university",
        "- voice_not_interested: User explicitly not interested",
        "- voice_immediate_hangup: User hangs up early",
        "- voice_wrong_number: Wrong number called",
        "- voice_no_action: Student already enrolled/in contact",
        "- voice_wants_call_back: User requests callback",
        "- voice_wants_email_follow_up: User wants email follow-up",
        "- voice_wants_whatsapp_sms_follow_up: User wants messaging follow-up",
        "- voice_voice_mail: Automated/voicemail response",
        "- voice_unknown: Doesn't fit other categories"
    ])
    
    return "\n".join(summary_lines)


def main():
    parser = argparse.ArgumentParser(description="Classify call transcript logs using GPT-5")
    parser.add_argument("log_file", help="Path to the log file containing transcripts")
    parser.add_argument("--api-key", help="OpenAI API key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--output", "-o", help="Output file for detailed results (JSON)")
    parser.add_argument("--summary-only", action="store_true", help="Only show summary, not individual results")
    
    args = parser.parse_args()
    
    # Setup OpenAI client
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key required. Set OPENAI_API_KEY environment variable or use --api-key")
        return 1
    
    client = openai.OpenAI(api_key=api_key)
    
    # Read transcripts
    try:
        transcripts = read_log_file(args.log_file)
        print(f"Found {len(transcripts)} transcripts to classify...")
    except FileNotFoundError:
        print(f"Error: Log file '{args.log_file}' not found")
        return 1
    except Exception as e:
        print(f"Error reading log file: {e}")
        return 1
    
    # Classify transcripts
    results = []
    classifications = Counter()
    
    for i, transcript in enumerate(transcripts, 1):
        if not args.summary_only:
            print(f"Processing transcript {i}/{len(transcripts)}...")
        
        intent = classify_transcript(client, transcript)
        classifications[intent] += 1
        
        results.append({
            "transcript_index": i,
            "transcript": transcript,
            "intent": intent,
            "classified_at": datetime.now().isoformat()
        })
    
    # Generate summary
    summary = generate_summary(classifications, len(transcripts))
    print("\n" + summary)
    
    # Save detailed results if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": dict(classifications),
                "total_transcripts": len(transcripts),
                "results": results,
                "generated_at": datetime.now().isoformat()
            }, f, indent=2)
        print(f"\nDetailed results saved to: {args.output}")
    
    return 0


if __name__ == "__main__":
    exit(main())