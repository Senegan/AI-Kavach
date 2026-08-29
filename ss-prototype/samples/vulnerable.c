#include <stdio.h>
#include <string.h>

void process_input(const char *input) {
    char buffer[16];

    // INTENTIONALLY VULNERABLE:
    // input is copied without checking its length.
    strcpy(buffer, input);

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
