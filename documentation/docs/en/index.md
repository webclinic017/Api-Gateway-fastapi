# Chepalopodus API Gateway
Gateway is a service that acts as an intermediary between various microservices, incorporating security and authentication measures. Additionally, it presents a set of additional features. It goes hand in hand with Vault and Administrator to function correctly.

## Features
- [x] **Websockets Request Intermediary:**
  - A Websockets request intermediary enables bidirectional real-time communication between clients and servers. This involves managing persistent connections, data transfer in both directions, and push notifications. Essential for real-time applications such as chats, online games, or collaborative applications.

- [x] **HTTP/HTTPS Request Intermediary:**
  - This component acts as an entry point for HTTP/HTTPS requests to your microservices. It performs tasks such as routing, filtering, authorization, and request logging, making it easy to control and manage incoming requests.

- [x] **PDF File Rendering Intermediary:**
  - The intermediary for rendering PDF files is responsible for generating PDF files from data or templates in other formats, such as HTML or Markdown. It can integrate with PDF generators and print servers to generate PDF documents on demand.

- [x] **Role-Based Authentication and Authorization with Groups and Systems:**
  - This component is responsible for authenticating users and authorizing their actions. It uses authentication mechanisms such as tokens, API keys, or user and password-based authentication. Authorization is based on roles, groups, or systems, meaning that users have specific permissions based on their identity or affiliation with groups or systems.

- [ ] **Authorization-Control on Microservices Endpoints through the Administration Page:**
  - Provides an administration interface through which you can configure and manage access authorization to various endpoints of your microservices. This allows defining who can access each resource and what operations they can perform.

- [ ] **Load Balancer:**
  - The load balancer evenly distributes requests among multiple instances of your microservices to ensure a uniform distribution of workload. This improves the availability, scalability, and performance of your services.

- [x] **Microservices Discovery:**
  - Facilitates the dynamic location of microservices in your environment. It uses mechanisms such as service registration and discovery so that microservices can find and communicate with each other efficiently. This is essential in microservices architectures.

- [x] **Connection with the Vault System for Registered Microservices Credential Management:**
  - Integrate your API Gateway with HashiCorp Vault to manage and secure the credentials and secrets used by your microservices. Vault provides a secure solution for storing and distributing secrets, such as database passwords, authentication tokens, and API keys.

- [x] **Request Limiting:**
  - Sets restrictions on the number of requests a client or user can make in a specific time period. This is used to prevent abuses, such as denial-of-service attacks or resource usage limitations.

## Important Notes
- This is a personal project where I attempt to simulate the functionality of well-known API Gateways, such as Kong or Keycloak.
- Since it runs with docker-compose, it should not be considered ready for production.
- The services are not yet 100% completed and are in a development stage.

## Initial Configuration

## General Diagram
![274782488-df5b13fc-61fe-4d87-9f1f-20db3be21320](https://github.com/ogarcia-dev/Gateway/assets/60816648/a1e423de-1290-4752-8718-2c263d6ff8ce)
