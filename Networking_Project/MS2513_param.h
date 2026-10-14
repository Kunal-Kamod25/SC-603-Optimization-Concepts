#ifndef MS2513_PARAM_H
#define MS2513_PARAM_H

#define MAX_HOSTS 26
#define BUF_SIZE 256

// Each Port simulates a data link with input and output buffers
typedef struct {
    int buffer[2][BUF_SIZE];  // [0] = out-buffer, [1] = in-buffer
} Port;

#endif