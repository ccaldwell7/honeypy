# honeypy

# What is a Honeypot?

A cybersecurity **honeypot** is a decoy system or network designed to attract and monitor malicious activity, such as cyberattacks. It simulates vulnerabilities to lure attackers, allowing security professionals to observe their methods and tactics without compromising critical systems.

### Key Features:

1. **Deception**: Appears as a legitimate system, such as a server or database, to attract attackers.
2. **Data Collection**: Gathers information about the attackers, their tools, and techniques.
3. **Risk Containment**: Isolated from real networks to prevent damage while still engaging with attackers.

### Purpose:

- **Threat Intelligence**: Helps understand emerging threats, attack vectors, and vulnerabilities.
- **Proactive Defense**: Identifies potential risks before they target critical systems.
- **Training**: Provides a controlled environment for cybersecurity teams to test responses to real-world attacks.

Honeypots are part of a broader strategy to strengthen an organization’s cybersecurity posture by turning attackers’ actions into valuable insights.

# Step 1: Creating Loggers

In order to complete this project, I followed along with Grant Collins on his honeypot crash course video. To start off this project I imported the python logging library and created two separate logging files as seen under my ‘Loggers & Logging Files’ comment section. This will allow for logs to be created with not only usernames, passwords, and ip addresses of potential attackers, but also showcase certain actions they may have taken.

# Step 2: Emulated Shell

The emulated_shell function simulates a shell environment for an SSH honeypot. It takes two parameters: channel, which represents the communication channel with the client, and client_ip, which is the IP address of the client. The function starts by sending a prompt (`corporate-jumpbox2$` ) to the client. It then enters an infinite loop where it listens for input from the client one byte at a time. Each received byte is echoed back to the client and appended to a command string. If no byte is received, the channel is closed.

When a carriage return (`\r`) is detected, indicating the end of a command, the function checks the command. If the command is `exit`, it sends a goodbye message and closes the channel. For the `pwd` command, it responds with a fake directory path (`\usr\local`). For the `whoami` command, it responds with a fake username (`corpuser1`). For the `ls` command, it responds with a fake file listing (`jumpbox1.conf`). For the `cat jumpbox1.conf` command, it responds with fake file content (`Go to crazy.com`). For any other command, it echoes the command back to the client. After handling the command, the command string is reset for the next input.

# Step 3: Building SSH Server

The Server class inherits from paramiko.ServerInterface and is used to handle SSH server interactions. The class is initialized with the client's IP address (client_ip), and optionally, a username (input_username) and password (input_password).

The check_channel_request method is called when a channel request is received. It checks the type of channel requested. If the request is for a "session" channel, it returns paramiko.OPEN_SUCCEEDED, indicating that the request is approved. Otherwise, it returns paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED, indicating that the request is denied.

The get_allowed_auths method returns the allowed authentication methods, which in this case is "password".

The check_auth_password method is called to authenticate a user. If the input_username and input_password are provided, it checks if the provided username and password match the expected values ('username' and 'password'). If they match, it returns paramiko.AUTH_SUCCESSFUL, indicating successful authentication. Otherwise, it returns paramiko.AUTH_FAILED, indicating failed authentication.

The check_channel_shell_request method is a placeholder for handling shell requests on the channel. 

# Step 4: Client Handle

At the end of the `# SSH Server & Sockets` section, the code handles exceptions and ensures that resources are properly closed:

- **Error Handling**: If an error occurs during the SSH session, a message "Error occurred." is printed.
- **Resource Cleanup**: In the `finally` block, the code attempts to close the transport and client connections:
    - **Transport Close**: It tries to close the transport object. If an exception occurs during this process, the error is printed along with the message "Error occurred while closing transport."
    - **Client Close**: The client connection is closed to ensure that all resources are properly released.

### **Provision SSH-based Honeypot**

The honeypot function sets up and runs the SSH honeypot:

- **Socket Setup**:
    - A new socket is created using socket.socket(socket.AF_INET, socket.SOCK_STREAM).
    - The socket option SO_REUSEADDR is set to allow the socket to be bound to an address that is in a `TIME_WAIT` state.
    - The socket is bound to the specified address and port using socks.bind((address, port)).
    - The socket starts listening for incoming connections with a backlog of 100 using socks.listen(100).
    - A message is printed to indicate that the honeypot is listening on the specified port.
- **Connection Handling Loop**:
    - The function enters an infinite loop to continuously accept incoming connections.
    - **Accepting Connections**: When a client connects, the socks.accept() method returns a new socket object (client) and the address of the client (addr).
    - **Thread Creation**: A new thread is created to handle the client connection using threading.Thread(target=client_handle, args=(client, addr, username, password)). The client_handle function is responsible for managing the interaction with the client.
    - **Thread Start**: The newly created thread is started using ssh_honeypot_thread.start().
    - **Error Handling**: If an exception occurs while accepting connections or starting the thread, the error is printed.

Finally, the honeypot function is called with the address `127.0.0.1`, port `2223`, and no specific username or password (username=None, password=None), starting the SSH honeypot on the local machine.

# Step 5: Argument Parser

To start a new file was set up, honeypy.py. 

This file serves as the main interface for running different types of honeypots. It imports necessary dependencies, parses command-line arguments, and starts the appropriate honeypot based on user input.

### Import Dependencies

- **Library Dependencies**: The argparse library is imported to handle command-line arguments.
- **Project Dependencies**: Various modules from the project are imported:
    - ssh_honeypot for SSH honeypot functionality.
    - web_honeypot for web-based honeypot functionality.
    - dashboard_data_parser for parsing data for the dashboard.
    - web_app for the web application interface.

### Main Functionality

The main functionality is enclosed within the if __name__ == "__main__": block to ensure it only runs when the script is executed directly.

- **Argument Parser Setup**:
    - An ArgumentParser object is created using parser = argparse.ArgumentParser().
    - Various arguments are added to the parser:
        - `a` or `-address`: The IP address to bind the honeypot to (required).
        - `p` or `-port`: The port to bind the honeypot to (required).
        - `u` or `-username`: The username for authentication (optional).
        - `w` or `-password`: The password for authentication (optional).
        - `s` or `-ssh`: A flag to indicate running an SSH honeypot.
        - `t` or `-tarpit`: A flag to enable tarpit functionality.
        - `wh` or `-http`: A flag to indicate running an HTTP honeypot.
- **Argument Parsing**:
    - The arguments are parsed using args = parser.parse_args().
- **Honeypot Selection**:
    - The script checks which honeypot to run based on the parsed arguments:
        - **SSH Honeypot**: If the `-ssh` flag is set (if args.ssh:):
            - A message "[-] Running SSH Honeypot..." is printed.
            - The honeypot function from ssh_honeypot is called with the provided address, port, username, password, and tarpit flag.
        - **HTTP Honeypot**: If the `-http` flag is set (elif args.http:):
            - A message "[-] Running HTTP Wordpress Honeypot..." is printed.
            - If no username is provided, it defaults to "admin" and prints a message indicating this.
            - If no password is provided, it defaults to "pw123".

The script ensures that the appropriate honeypot is started based on user input, with default values for username and password if not provided.

# Step 6: Web Honeypot

### **Web Honeypot Implementation**

The web_honeypot.py file sets up a simple web-based honeypot using Flask. It simulates a fake WordPress admin login page to capture login attempts and log the credentials entered by potential attackers.

### Flask Application Setup

- **Route Definitions**:
    - **Index Route** (`/`):
        - The index function renders and returns the `wp-admin.html` template when the root URL is accessed. This simulates the WordPress admin login page.
    - **Login Route** (`/wp-admin-login`):
        - The login function handles POST requests to the `/wp-admin-login` URL.
        - It retrieves the username and password from the form data submitted by the client.
        - It captures the client's IP address using request.remote_addr.
        - The login attempt, including the IP address, username, and password, is logged using funnel_logger.
        - The function checks if the entered username and password match the expected values (input_username and input_password). If they match, it returns "Login successful!". Otherwise, it returns "Login failed!".

### Running the Web Honeypot

- **run_web_honeypot Function**:
    - The run_web_honeypot function initializes and runs the Flask application.
    - It takes optional parameters for the port (port), username (input_username), and password (input_password), with default values of 5000, "admin", and "password" respectively.
    - The function creates an instance of the web honeypot application by calling web_honeypot(input_username, input_password).
    - It runs the Flask application in debug mode, listening on all network interfaces (host="0.0.0.0") and the specified port.
    - The function returns the Flask application instance.

This file sets up a basic web honeypot that captures and logs login attempts to a fake WordPress admin page, providing valuable information about potential attackers.
