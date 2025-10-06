#!/usr/bin/env python3
"""
Test Each Improvement Individually

Tests:
1. Baseline (original simple prompt)
2. Different prompt variations
3. Few-shot learning
4. Chain-of-thought reasoning
5. Ensemble voting
"""

import json
import os
import argparse
import csv
import random
import uuid
from datetime import datetime
from collections import Counter
from typing import Dict, List
import openai
from concurrent.futures import ThreadPoolExecutor, as_completed


class ImprovementTester:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = "gpt-5-mini-2025-08-07"
    
    # 1. BASELINE - Original simple prompt
    def baseline_classify(self, transcript: str) -> Dict:
        """Original simple prompt from classify_logs.py"""
        system_prompt = f"""
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

<!-- Cache buster: {uuid.uuid4()} -->
"""
        
        user_prompt = f"""
Transcript:
--- BEGIN TRANSCRIPT ---
{transcript}
--- END TRANSCRIPT ---

Remember to focus on the User's replies to derive their intent, and not the Agent's!
Reply in the following JSON format {{'intent': <category>}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
            )
            result = json.loads(response.choices[0].message.content)
            return {"intent": result.get("intent", "voice_unknown"), "method": "baseline"}
        except Exception as e:
            return {"intent": "voice_unknown", "method": "baseline", "error": str(e)}
    
    # 2. DIFFERENT PROMPT - More conversational
    def different_prompt_classify(self, transcript: str) -> Dict:
        """More conversational prompt style"""
        system_prompt = f"""
You're helping analyze phone calls between education advisors and prospective students.

Your job: Figure out what the person who answered (the "User") actually wants.

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

<!-- Cache buster: {uuid.uuid4()} -->
"""
        
        user_prompt = f"""Phone conversation:

{transcript}

What does the User want? Respond in JSON: {{"intent": "<category>"}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
            )
            result = json.loads(response.choices[0].message.content)
            return {"intent": result.get("intent", "voice_unknown"), "method": "different_prompt"}
        except Exception as e:
            return {"intent": "voice_unknown", "method": "different_prompt", "error": str(e)}
    
    # 3. FEW-SHOT LEARNING
    def few_shot_classify(self, transcript: str) -> Dict:
        """Original prompt + few-shot examples"""
        system_prompt = """
You are responsible for classifying incoming call transcripts into relevant intent types.
Focus exclusively on the user's reply (sentences starting with 'User:').

Categories:
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
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add 2 correctly classified examples from the original dataset
        user_prompt = f"""Here are 2 examples of correct classifications:

Example 1:
Transcript: User: Hello?
Agent: Hi 
User: Hello? 
Agent: Wai Kit, this is James from Kaplan. Do you have a minute to chat?
User: No. Sorry. Can you call back another day?
Agent: No problem at all! When would be a good day 
User: Thank you. 
Agent: for me to call 
User: Bye bye.
User: Thank you. Bye bye.

Correct classification: {{"intent": "voice_wants_call_back"}}

Example 2:
Transcript: User: Hello?
Agent: Hi Siti! This is James from Kaplan. Do 
User: Say 
Agent: you have a quick minute to chat?
User: again?
Agent: Hi Siti, this is James from Kaplan Singapore. Do you have a moment to chat?
User: Yes.
Agent: Great! I wanted to check if you are still interested in pursuing the Bachelor of Marketing degree at Global University?
User: It's Because I still need to check on my ABL that security, may I know when is the next Next, we'll go date to enter.
Agent: Global University has three intakes each year—in January, May, and September. Would you like me to set up a call with your advisor to discuss this further? They can guide you on the next steps.
User: Okay. But if were to join, most probably, I will be joining during September.
Agent: That sounds like a good plan! September gives you plenty of time to prepare. Would you like me to schedule a call with your advisor to discuss your application and any other details?
Agent: Just checking in—would you like me to arrange a call with your advisor to help you with the September intake and any other questions you might have?
User: Yes, please.

Correct classification: {{"intent": "voice_interested"}}

Now classify this transcript:
Transcript: {transcript}

Reply in JSON: {{"intent": "<category>"}}

<!-- Cache buster: {uuid.uuid4()} -->"""

        messages.append({
            "role": "user",
            "content": user_prompt
        })
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
            )
            result = json.loads(response.choices[0].message.content)
            return {"intent": result.get("intent", "voice_unknown"), "method": "few_shot"}
        except Exception as e:
            return {"intent": "voice_unknown", "method": "few_shot", "error": str(e)}
    
    # 4. CHAIN-OF-THOUGHT
    def chain_of_thought_classify(self, transcript: str) -> Dict:
        """Original prompt + ask model to think step by step"""
        system_prompt = """
You are responsible for classifying call transcripts. Focus only on User statements.

Categories: voice_interested, voice_not_interested, voice_immediate_hangup, voice_wrong_number, 
voice_no_action, voice_wants_call_back, voice_wants_email_follow_up, 
voice_wants_whatsapp_sms_follow_up, voice_voice_mail, voice_unknown
"""
        
        user_prompt = f"""Transcript: {transcript}

Think step by step:
1. What did the User actually say?
2. What is their clear intent?
3. Which category fits best?

Respond in JSON: {{"intent": "<category>", "reasoning": "<brief explanation>"}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            return {"intent": result.get("intent", "voice_unknown"), "method": "chain_of_thought"}
        except Exception as e:
            return {"intent": "voice_unknown", "method": "chain_of_thought", "error": str(e)}
    
    # 5. ENSEMBLE (3 instances of few-shot voting)  
    def ensemble_classify(self, transcript: str) -> Dict:
        """Run 3 instances of few-shot method and vote"""
        # Get results from 3 instances of the same few-shot method
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(self.few_shot_classify, transcript),
                executor.submit(self.few_shot_classify, transcript),
                executor.submit(self.few_shot_classify, transcript)
            ]
            
            results = []
            for i, future in enumerate(futures):
                try:
                    result = future.result()
                    result["instance"] = f"few_shot_{i+1}"
                    results.append(result)
                except Exception as e:
                    results.append({"intent": "voice_unknown", "instance": f"few_shot_{i+1}", "error": str(e)})
        
        # Vote on result
        intents = [r["intent"] for r in results]
        intent_counts = Counter(intents)
        most_common = intent_counts.most_common(1)[0][0]
        
        return {
            "intent": most_common,
            "method": "ensemble_few_shot",
            "votes": dict(intent_counts),
            "individual_results": results
        }
    
    def run_method(self, method_name: str, transcripts: List[str]) -> List[Dict]:
        """Run a specific method on all transcripts"""
        method_map = {
            "baseline": self.baseline_classify,
            "different_prompt": self.different_prompt_classify,
            "few_shot": self.few_shot_classify,
            "chain_of_thought": self.chain_of_thought_classify,
            "ensemble": self.ensemble_classify
        }
        
        classify_func = method_map[method_name]
        results = []
        
        print(f"Running {method_name} method...")
        
        # Use parallel processing
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_index = {
                executor.submit(classify_func, transcript): i 
                for i, transcript in enumerate(transcripts)
            }
            
            completed_results = {}
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    result = future.result()
                    completed_results[index] = {
                        "transcript_index": index + 1,
                        "transcript": transcripts[index],
                        "classification_result": result,
                        "classified_at": datetime.now().isoformat()
                    }
                except Exception as e:
                    completed_results[index] = {
                        "transcript_index": index + 1,
                        "transcript": transcripts[index],
                        "classification_result": {"intent": "voice_unknown", "error": str(e)},
                        "classified_at": datetime.now().isoformat()
                    }
        
        return [completed_results[i] for i in range(len(transcripts))]


def read_csv_transcripts(file_path: str) -> List[str]:
    """Read transcripts from CSV"""
    transcripts = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            transcript = row.get('transcript', '')
            if transcript:
                transcripts.append(transcript)
    return transcripts


def evaluate_accuracy(results: List[Dict], ground_truth: Dict[int, str]) -> float:
    """Calculate accuracy against ground truth"""
    correct = 0
    total = len(results)
    
    for result in results:
        idx = result['transcript_index']
        predicted = result['classification_result']['intent']
        human = ground_truth[idx]
        
        if predicted == human:
            correct += 1
    
    return correct / total * 100 if total > 0 else 0


def main():
    parser = argparse.ArgumentParser(description="Test each improvement individually")
    parser.add_argument("csv_file", help="Path to CSV file")
    parser.add_argument("--api-key", help="OpenAI API key")
    parser.add_argument("--method", choices=["baseline", "different_prompt", "few_shot", "chain_of_thought", "ensemble", "all"], 
                        default="all", help="Which method to test")
    
    args = parser.parse_args()
    
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key required")
        return 1
    
    # Load data
    transcripts = read_csv_transcripts(args.csv_file)
    
    # Load ground truth
    ground_truth = {}
    with open(args.csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            ground_truth[i] = row['human_generated_intent']
    
    tester = ImprovementTester(api_key)
    
    methods_to_test = ["baseline", "different_prompt", "few_shot", "chain_of_thought", "ensemble"] if args.method == "all" else [args.method]
    
    results_summary = {}
    
    for method in methods_to_test:
        print(f"\n{'='*60}")
        print(f"TESTING: {method.upper()}")
        print(f"{'='*60}")
        
        start_time = datetime.now()
        results = tester.run_method(method, transcripts)
        end_time = datetime.now()
        
        accuracy = evaluate_accuracy(results, ground_truth)
        duration = (end_time - start_time).total_seconds()
        
        results_summary[method] = {
            "accuracy": accuracy,
            "duration": duration,
            "correct": int(accuracy * len(transcripts) / 100),
            "total": len(transcripts)
        }
        
        print(f"Accuracy: {accuracy:.1f}% ({int(accuracy * len(transcripts) / 100)}/{len(transcripts)})")
        print(f"Duration: {duration:.1f}s")
        
        # Save detailed results with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"test_{method}_{timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump({
                "method": method,
                "accuracy": accuracy,
                "duration": duration,
                "results": results,
                "generated_at": datetime.now().isoformat()
            }, f, indent=2)
        print(f"Saved: {output_file}")
    
    # Final comparison
    if len(methods_to_test) > 1:
        print(f"\n{'='*60}")
        print("FINAL COMPARISON")
        print(f"{'='*60}")
        print(f"{'Method':<20} {'Accuracy':<12} {'Time':<10} {'Notes'}")
        print("-" * 60)
        
        for method, stats in results_summary.items():
            notes = "baseline" if method == "baseline" else f"{stats['accuracy'] - results_summary['baseline']['accuracy']:+.1f}pp vs baseline"
            print(f"{method:<20} {stats['accuracy']:>6.1f}%     {stats['duration']:>6.1f}s   {notes}")
    
    return 0


if __name__ == "__main__":
    exit(main())