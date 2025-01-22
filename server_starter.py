from aiosmtpd.controller import Controller

class ExampleHandler:
    async def handle_DATA(self, server, session, envelope):
        """
        Handle incoming emails.
        This method is called whenever an email is received.
        """
        print("\n---------- MESSAGE FOLLOWS ----------")
        print(f"From: {envelope.mail_from}")
        print(f"To: {envelope.rcpt_tos}")
        print(f"Message data:\n{envelope.content.decode('utf-8')}")
        print("------------ END MESSAGE ------------\n")
        return '250 OK'  # Acknowledge receipt of the email

def start_smtp_server(host='127.0.0.1', port=1025):
    """
    Start the SMTP server.
    """
    # Create a controller to manage the SMTP server
    controller = Controller(ExampleHandler(), hostname=host, port=port)
    
    # Start the server
    controller.start()
    print(f"SMTP server running on {host}:{port}")
    
    try:
        # Keep the server running until the user presses Enter
        input("Press Enter to stop the server...\n")
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    finally:
        # Stop the server
        controller.stop()
        print("SMTP server stopped.")

if __name__ == "__main__":
    # Start the SMTP server on localhost:1025
    start_smtp_server(host='127.0.0.1', port=1025)