# Crypto-Proj-2025

Crypto &amp; Network Security Project 2025

Cryptography and Network Security I
Spring 2025
Project Description

This is a group (2-3 students) project and you are free to choose your team mates.

You (as a group) will be implementing your own version of SSH/SSL protocol which supports your own implementation of the ciphers including the symmetric key ones (e.g., DES), PKC under ciphertext only adversary, semantically secure PKC, and homomorphic cipher as we discussed in the class and you implemented in homeworks. For digital signature schemes, use one that is based on PKC, for MAC use HMAC, for hash functions use SHA. You will have to implement your own random number generators.

The project will be implemented as a client-server protocol to mimic transactions/ebanking between an ATM (client) and the bank (server). Your project will enable banking operations to deposit, withdraw money, and check balance via ATM by accessing the bank.

You are allowed to use sockets programming libraries. You can use already implemented tools for
primality testing, integer factorization, discrete logarithm. You cannot use already implemented ciphers.
Each team will play white hat and black hat roles as described below:

TIME LINE & Grading:

White-hat part [60 points] due 11:59AM, April 15, 2025: The goal is to

    (i) [20pnts] negotiate and establish a secure channel using the SSL/SSH handshake protocol.
        a. Cyphertext only threat model is the minimum requirement to be met. ECC implementation is
        required.
        b. Students who registered for the graduate level will have to implement PKC systems to defend
        against to IND-CPA, IND-CCA threat models. This is optional for undergraduate level but improves
        the grade.

    (ii) [20pnts] pass back and forth messages to implement the banking operations above.

    (iii) [20pnts] You will write a document explaining your implementation as a part of your communication
        intensive requirement and pass the code to the TA.
        We will assign your code a Black-hat team to analyze and attack. If your code does not run than black-hat
        will get the full points (since they can claim whatever they want) ☺.

Black-hat part [40 points] due 11:59pm, April 21, 2025: you will receive the source code of the target
team on April 15, 11:59PM, 2025. Your goal is to find weaknesses in the implementation of

    (i) cryptographic primitives and protocols [20pnts]

    (ii) write a report on your attacks as a part of your communication intensive requirement.

In class presentation [100 points] April 22-23, 2025: we will schedule a time slot for each group for
presentations and demos.
