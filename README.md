# v2itollpaymentprototype
### V2I-Based Automatic Toll Payment System 🚗🏁
The V2I-based automatic toll payment system consists of an integration of several key components, including hardware, software, and a wireless network communication model. The first stage of implementation begins with hardware development, comprising the On-Board Unit (OBU) and the Roadside Unit (RSU), with the OBU utilizing the Raspberry Pi 5 as its main platform, featuring:
1. NFC card reading on the vehicle side (OBU)
2. Secure TLS socket communication between OBU and RSU
3. Wi-Fi authentication using FreeRADIUS
4. Balance deduction handled by a MongoDB-based backend
5. Performance measurement of delay, throughput, and avalanche effect

### System Architecture
<img width="776" height="231" alt="image" src="https://github.com/user-attachments/assets/cd5f6d6b-4679-462c-911b-c2ff6468da57" />
The system architecture illustrates the interconnection between the three main components with clearly defined communication protocols. The On-Board Unit (OBU) communicates with the Roadside Unit (RSU) over a local Wi-Fi network secured by RADIUS authentication, while the RSU is integrated with a backend server for transaction data synchronizatio. This section provides a detailed explanation of the implementation process and outcomes of the Vehicle-to-Infrastructure (V2I) communication system, developed to address traffic congestion issues at toll gates through wireless communication between vehicles (OBU) and roadside infrastructure (RSU). The system consists of two main components: the On-Board Unit (OBU) and the Roadside Unit (RSU).
