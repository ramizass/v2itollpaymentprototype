# v2itollpaymentprototype
### V2I-Based Automatic Toll Payment System 🚗🏁
The V2I-based automatic toll payment system consists of an integration of several key components, including hardware, software, and a wireless network communication model. The first stage of implementation begins with hardware development, comprising the On-Board Unit (OBU) and the Roadside Unit (RSU), with the OBU utilizing the Raspberry Pi 5 as its main platform, featuring:
1. NFC card reading on the vehicle side (OBU)
2. Secure TLS socket communication between OBU and RSU
3. Wi-Fi authentication using FreeRADIUS
4. Balance deduction handled by a MongoDB-based backend
5. Performance measurement of delay, throughput, and avalanche effect

### System Architecture
<img width="674" height="246" alt="Picture1" src="https://github.com/user-attachments/assets/b59accb2-d289-4f28-a876-a128e44e662d" />
<img width="841" height="513" alt="image" src="https://github.com/user-attachments/assets/473cace7-d283-445e-a9da-50af21c4057b" />


The system architecture illustrates the interconnection between the three main components with clearly defined communication protocols. The On-Board Unit (OBU) communicates with the Roadside Unit (RSU) over a local Wi-Fi network secured by RADIUS authentication, while the RSU is integrated with a backend server for transaction data synchronization. 
