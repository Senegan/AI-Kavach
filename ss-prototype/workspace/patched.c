#include <stdio.h>
#include <string.h>

void process_input(const char *input) {
    char buffer[16];

    // Fixed vulnerability: use strncpy to avoid buffer overflow
    strncpy(buffer, input, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\0';

    printf("Processed: %s\n", buffer);
}

int main(int argc, char **argv) {
    if (argc != 2) {
        printf("Usage: %s <input>\n", argv[0]);
        return 1;
    }

    process_input(argv[1]);

    return 0;
}