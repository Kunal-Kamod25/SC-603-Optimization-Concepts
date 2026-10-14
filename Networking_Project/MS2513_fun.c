#include "MS2513_fun.h"

// Global Ports for Test Programs, Link Layer, and LAN
Port TestP[MAX_HOSTS];
Port LLL[MAX_HOSTS];
Port LAN[MAX_HOSTS];
int numHosts;

// Initialize all buffers to zero
void initialize(int n) {
    for (int i = 0; i < n; i++) {
        TestP[i].buffer[0][0] = TestP[i].buffer[1][0] = 0;
        LLL[i].buffer[0][0] = LLL[i].buffer[1][0] = 0;
        LAN[i].buffer[0][0] = LAN[i].buffer[1][0] = 0;
    }
    printf("\n Buffers initialized for %d hosts.\n", n);
}

// Connectors: Transfer data between two layers
void connectors(Port P1[], Port P2[], int n) {
    for (int i = 0; i < n; i++) {
        if (P1[i].buffer[0][0] > 0 && P2[i].buffer[1][0] == 0) {
            int bc = P1[i].buffer[0][0];
            for (int j = 0; j <= bc; j++)
                P2[i].buffer[1][j] = P1[i].buffer[0][j];
            P1[i].buffer[0][0] = 0; // Clear after transfer
        }
    }
}

// Application Layer (TestP): Generates and receives packets
void testPStrip(int id, int n) {
    // Receiving packets
    if (TestP[id].buffer[1][0] > 0) {
        printf(" TestP[%d] received: [NetID:%d, MachID:%d] ",
               id + 1,
               TestP[id].buffer[1][1],
               TestP[id].buffer[1][2]);

        for (int j = 3; j <= TestP[id].buffer[1][0]; j++)
            printf("%c", TestP[id].buffer[1][j]);

        printf("\n");
        TestP[id].buffer[1][0] = 0;
    }

    // 10% chance to generate a new packet
    if (rand() % 100 < 10) {
        int payload = 13 + rand() % 8;
        int bc = payload + 3; // 3 bytes: NetID, MachID, Type

        TestP[id].buffer[0][0] = bc;
        TestP[id].buffer[0][1] = rand() % 10; // Network ID (numeric)
        TestP[id].buffer[0][2] = rand() % 10; // Machine ID (numeric)
        TestP[id].buffer[0][3] = 'D';         // Data Type

        for (int i = 4; i <= bc; i++)
            TestP[id].buffer[0][i] = 'a' + (rand() % 26);

        printf(" TestP[%d] generated a packet (%d bytes)\n", id + 1, bc);
    }
}

// Data Link Layer (LLL)
void LLLStrip(int id, int n) {
    if (LLL[id].buffer[1][0] > 0) {
        int bc = LLL[id].buffer[1][0];

        if (!isalpha(LLL[id].buffer[1][1])) {
         
            int dest;
            do {
                dest = rand() % n;
            } while (dest == id);

            char smac = 'A' + id;
            char dmac = 'A' + dest;

            LLL[id].buffer[0][0] = bc + 2;
            LLL[id].buffer[0][1] = dmac;
            LLL[id].buffer[0][2] = smac;

            for (int j = 1; j <= bc; j++)
                LLL[id].buffer[0][j + 2] = LLL[id].buffer[1][j];

            printf(" LLL[%d]: Added [DMAC:%c, SMAC:%c] for Host %d\n",
                   id + 1, dmac, smac, dest + 1);
        } else {
            // From LAN, check destination MAC
            char dmac = LLL[id].buffer[1][1];
            if (dmac == ('A' + id)) {
                int newLen = bc - 2;
                LLL[id].buffer[0][0] = newLen;

                for (int j = 1; j <= newLen; j++)
                    LLL[id].buffer[0][j] = LLL[id].buffer[1][j + 2];

                printf(" LLL[%d]: Packet accepted for TestP[%d]\n", id + 1, id + 1);
            } else {
                printf(" LLL[%d]: Packet dropped (Not for this host)\n", id + 1);
            }
        }
        LLL[id].buffer[1][0] = 0;
    }
}

// LAN Layer: Broadcast + Collision Detection
void LANStrip(int n) {
    int senders = 0, senderIndex = -1;

    for (int i = 0; i < n; i++) {
        if (LAN[i].buffer[1][0] > 0) {
            senders++;
            senderIndex = i;
        }
    }

    if (senders > 1) {
        printf("  Collision detected! Data lost.\n");
        for (int i = 0; i < n; i++)
            LAN[i].buffer[1][0] = 0;
        return;
    }

    if (senders == 1) {
        int bc = LAN[senderIndex].buffer[1][0];
        for (int i = 0; i < n; i++) {
            if (i != senderIndex) {
                for (int j = 0; j <= bc; j++)
                    LAN[i].buffer[0][j] = LAN[senderIndex].buffer[1][j];
            }
        }
        printf(" LAN: Broadcasted packet from Host%d to all others.\n", senderIndex + 1);
        LAN[senderIndex].buffer[1][0] = 0;
    } else {
        printf("  LAN: Idle, no active transmission.\n");
    }
}

// Round Robin Scheduler
void scheduler() {
    printf("\n enter number of hosts (3 to %d): ", MAX_HOSTS);
    scanf("%d", &numHosts);
    if (numHosts < 3 || numHosts > MAX_HOSTS) numHosts = 3;

    srand(time(0));
    initialize(numHosts);

    int round = 1;
    char choice;

    while (1) {
        printf("\n================ ROUND %d ================\n", round);

        for (int i = 0; i < numHosts; i++) testPStrip(i, numHosts);
        connectors(TestP, LLL, numHosts);

        for (int i = 0; i < numHosts; i++) LLLStrip(i, numHosts);
        connectors(LLL, LAN, numHosts);

        LANStrip(numHosts);
        connectors(LAN, LLL, numHosts);

        for (int i = 0; i < numHosts; i++) LLLStrip(i, numHosts);
        connectors(LLL, TestP, numHosts);

        printf("Continue simulation? (q to quit): ");
        scanf(" %c", &choice);
        if (choice == 'q' || choice == 'Q') {
            printf("\n Simulation ended. Thank you!\n");
            break;
        }
        round++;
    }
}