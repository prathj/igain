import random
import re
import logging
import backoff

# for logging errors and api calls
logger = logging.getLogger(__name__)

# class to model chatbot instance
class ChatBot:
    def __init__(self, openai_client):
        self.client = openai_client
        self.reset()
        # state attribute to determine current point of conversation in chatbot
        self.state_handlers = {
            "greeting": self.state_greeting,
            "awaiting_tracking": self.state_awaiting_tracking,
            "awaiting_alternative_info": self.state_awaiting_alternative_info,
            "tracking_confirmed": self.state_tracking_confirmed,
            "filing_ticket": self.state_filing_ticket,
            "finalizing": self.state_finalizing,
            "end": self.state_end,
        }
    
    # resets conversation
    def reset(self):
        self.conversation_history = [
            {
                "role": "system",
                "content": (
                    "You are a customer support chatbot specialized in tracking lost packages. "
                    "Your task is to ask for tracking numbers or order IDs, validate the data, "
                    "provide package status, and offer creative options like real-time updates, "
                    "filing a support ticket, or escalating issues. Keep your tone friendly and clear."
                )
            }
        ]
        self.current_state = "greeting"
    
    # call to api with exponential backoff to a avoid rate limiting
    @backoff.on_exception(backoff.expo, 
                         (Exception),
                         max_tries=5,
                         giveup=lambda e: "maximum context length" in str(e).lower(),
                         on_backoff=lambda details: logger.info(f"Backing off {details['wait']:0.1f} seconds after {details['tries']} tries"))
    def _create_chat_completion(self, messages):
        """Protected method to create chat completion with exponential backoff"""
        return self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
    
    # get response from api call
    def generate_response(self, prompt_context):
        if self.client is None:
            return "Sorry, there's an issue with our AI service at the moment. Please try again later."
        try:
            response = self._create_chat_completion(prompt_context)
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response after retries: {str(e)}")
            error_msg = str(e).lower()
            if "rate limit" in error_msg:
                return "We're experiencing high demand right now. Please try again in a moment."
            elif "maximum context length" in error_msg:
                return "Token limit reached. Ending conversation."
            else:
                return f"An unexpected error occurred: {str(e)}"
    
    # openai API's decisio on what branch to go to
    def decide_branch(self, prompt):
        messages = [{"role": "system", "content": prompt}]
        decision = self.generate_response(messages)
        return decision.strip().lower()
    
    # --- State handler methods ---
    
    # initial greeting to user
    def state_greeting(self, user_input):
        response = "Hello! I'm here to help you track your package. Could you please provide your tracking number or order ID?"
        self.current_state = "awaiting_tracking"
        self.conversation_history.append({"role": "assistant", "content": response})
        return response
    
    # get tracking number from user input
    def extract_tracking_number(self, user_input):
        # Find all digit sequences in the input.
        numbers = re.findall(r'\d+', user_input)
        # look for any string that is exactly 10 or 12 digits
        for num in numbers:
            if len(num) in [10, 12]:
                return num
        return None
    
    # if valid tracking number is given by user, then they are prompted to either want updates or assistance filing a ticket
    # otherwise, openai used to determine if user wants to provide additional information or other edge cases
    def state_awaiting_tracking(self, user_input):
        # try to first get a valid tracking number
        tracking_number = self.extract_tracking_number(user_input)
        if tracking_number:
            response = (f"Great, tracking number {tracking_number} confirmed. Your package encountered some shipping delays but is now currently in transit. "
                        "Would you like real-time updates or assistance filing a support ticket?")
            self.current_state = "tracking_confirmed"
            self.conversation_history.append({"role": "assistant", "content": response})
            return response
        else:
            # otherwise, let GPT decide the branch.
            prompt = (
                "You are a decision-making assistant for a package tracking chatbot. "
                "The current state is 'awaiting_tracking'. The user provided: "
                f'"{user_input}".\n\n'
                "Decide which branch to follow. Options are:\n"
                "1. 'invalid_tracking' if the input contains a number.\n"
                "2. 'alternative_info' if the user indicates they don't have a tracking number.\n"
                "3. 'restart' if the user wants to restart the conversation.\n"
                "4. 'invalid' if the input is irrelevant or does not match the expected format.\n\n"
                "Respond with only one of these words: invalid_tracking, alternative_info, restart, or invalid."
            )
            branch = self.decide_branch(prompt)
            if branch == "restart":
                return self.state_greeting(user_input)
            elif branch == "alternative_info":
                response = "I understand you don't have a tracking number. Could you please provide your email or name?"
                self.current_state = "awaiting_alternative_info"
            elif branch == "invalid_tracking":
                response = "Your tracking number must be 10 or 12 digits"
            elif branch == "invalid":
                response = "That doesn't look right, please provide the information requested."
                self.current_state = "awaiting_tracking"
            else:
                response = "I'm sorry, I couldn't determine your input. Please rephrase your tracking number or indicate if you don't have it."
            self.conversation_history.append({"role": "assistant", "content": response})
            return response
    
    # gpt decides if valid alternative info is given, a random order number is generated for the user
    # otherwise if other info is given, then keep requesting info or restart conversation
    def state_awaiting_alternative_info(self, user_input):
        prompt = (
            "You are a decision-making assistant for a package tracking chatbot. "
            "The current state is 'awaiting_alternative_info'. The user provided: "
            f'"{user_input}".\n\n'
            "Decide if this alternative information (email or name) is valid. Options are:\n"
            "1. 'valid_alternative' if the input is valid identifying information.\n"
            "2. 'invalid' if the input is not acceptable.\n"
            "3. 'restart' if the user wants to restart the conversation.\n\n"
            "Respond with only one of these words: valid_alternative, invalid, or restart."
        )
        branch = self.decide_branch(prompt)
        if branch == "restart":
            return self.state_greeting(user_input)
        elif branch == "valid_alternative":
            order_number = str(random.randint(1000000000, 9999999999))
            response = (f"Great, tracking number {order_number} confirmed. Your package encountered some shipping delays but is now currently in transit. "
                        "Would you like real-time updates or assistance filing a support ticket?")
            self.current_state = "tracking_confirmed"
        elif branch == "invalid":
            response = "That doesn't look right, please provide the information requested."
            self.current_state = "awaiting_alternative_info"
        else:
            response = "I'm sorry, I couldn't understand that. Please provide the information requested."
            self.current_state = "awaiting_alternative_info"
        self.conversation_history.append({"role": "assistant", "content": response})
        return response
    
    # gpt decides if user wants to file a ticket or get updates on their order
    def state_tracking_confirmed(self, user_input):
        if user_input.strip().lower() == "restart":
            return self.state_greeting(user_input)
        prompt = (
            "You are a decision-making assistant for a package tracking chatbot in state 'tracking_confirmed'. "
            "The user provided: " f'"{user_input}".\n\n'
            "Decide which branch to follow. Options are:\n"
            "1. 'filing_ticket' if the user wants to file a support ticket.\n"
            "2. 'finalizing' if the user wants to receive real-time updates and finalize the conversation.\n"
            "3. 'restart' if the user wants to restart.\n"
            "4. 'invalid' if the input is irrelevant.\n\n"
            "Respond with only one of these words: filing_ticket, finalizing, restart, or invalid."
        )
        decision = self.decide_branch(prompt)
        if decision == "filing_ticket":
            response = "I can help file a support ticket. Please provide more details about the issue."
            self.current_state = "filing_ticket"
        elif decision == "finalizing":
            response = "Great! I'll send you real-time update to the email associated with the order. Are you still in need of assistance?"
            self.current_state = "finalizing"
        elif decision == "restart":
            response = self.state_greeting(user_input)
        elif decision == "invalid":
            response = "That doesn't look right, please provide the information requested."
        else:
            response = "I'm sorry, I didn't understand. Please provide either updates or ticket help."
        self.conversation_history.append({"role": "assistant", "content": response})
        return response
    
    # based on user input, a "ticket is created"
    def state_filing_ticket(self, user_input):
        if user_input.strip().lower() == "restart":
            return self.state_greeting(user_input)
        response = (f"Thanks for the details. I've filed a support ticket regarding: '{user_input}'. "
                    "Our team will follow up shortly at the email associated with your order. Are you still in need of assistance?")
        self.current_state = "finalizing"
        self.conversation_history.append({"role": "assistant", "content": response})
        return response
    
    # if user still needs help, they indicate so and are sent back to the state deciding if they want to file a ticket or get updates
    def state_finalizing(self, user_input):
        if user_input.strip().lower() == "restart":
            return self.state_greeting(user_input)
        
        # check for "no" answer to end the conversation.
        if user_input.strip().lower() == "no":
            response = "Thank you for using our service. Goodbye!"
            self.current_state = "end"
            self.conversation_history.append({"role": "assistant", "content": response})
            return response
        
        # check for "yes" answer to end the conversation.
        if user_input.strip().lower() == "yes":
            response = "Okay, let's continue. Would you like real-time updates or assistance filing a support ticket?"
            self.current_state = "tracking_confirmed"
            self.conversation_history.append({"role": "assistant", "content": response})
            return response
        
        prompt = (
            "You are a decision-making assistant for a package tracking chatbot in state 'finalizing'. "
            "The user provided: " f'"{user_input}".\n\n'
            "Decide if the conversation should continue or end. Options are:\n"
            "1. 'continue' if the user still needs assistance.\n"
            "2. 'end' if the conversation should end.\n"
            "3. 'restart' if the user wants to restart.\n\n"
            "Respond with only one of these words: continue, end, or restart."
        )
        decision = self.decide_branch(prompt)
        if decision == "continue":
            response = "Okay, let's continue. Would you like real-time updates or assistance filing a support ticket?"
            self.current_state = "tracking_confirmed"
        elif decision == "end":
            response = "Thank you for using our service. Goodbye!"
            self.current_state = "end"
        elif decision == "restart":
            response = self.state_greeting(user_input)
        else:
            response = "That doesn't look right, please provide the information requested."
            self.current_state = "finalizing"
        self.conversation_history.append({"role": "assistant", "content": response})
        return response
    
    # ends conversation, can be refreshed from here
    def state_end(self, user_input=None):
        return "The conversation has ended. Please restart if you need further assistance."
    
    def process_input(self, user_input):
        self.conversation_history.append({"role": "user", "content": user_input})
        handler = self.state_handlers.get(self.current_state, self.state_end)
        return handler(user_input)
