/* Linux/POSIX user-space exercise, not a kernel driver or serial configuration.
 * stdin: newline-delimited records; max 80 bytes excluding newline.
 * Overlong records are discarded through the next newline, not split as valid.
 */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <poll.h>
#include <stdio.h>
#include <unistd.h>

int main(void)
{
    char line[80];
    char chunk[64];
    size_t used = 0;
    int discarding = 0;
    struct pollfd input = { .fd = STDIN_FILENO, .events = POLLIN };
    for (;;) {
        int ready = poll(&input, 1, 2000);
        if (ready < 0) {
            if (errno == EINTR) continue;
            perror("poll"); return 1;
        }
        if (ready == 0) { fputs("idle timeout\n", stderr); continue; }
        if (input.revents & (POLLERR | POLLNVAL)) {
            fputs("input error\n", stderr); return 1;
        }
        if (!(input.revents & (POLLIN | POLLHUP))) continue;
        /* Consume final buffered bytes even when HUP is reported. */
        ssize_t count = read(STDIN_FILENO, chunk, sizeof chunk);
        if (count < 0) {
            if (errno == EINTR || errno == EAGAIN) continue;
            perror("read"); return 1;
        }
        if (count == 0) {
            if (used || discarding) fputs("truncated record at EOF\n", stderr);
            return (used || discarding) ? 2 : 0;
        }
        for (ssize_t i = 0; i < count; ++i) {
            if (chunk[i] == '\n') {
                if (!discarding) {
                    if (fwrite(line, 1, used, stdout) != used || putchar('\n') == EOF) return 1;
                }
                used = 0; discarding = 0;
            } else if (!discarding) {
                if (used == sizeof line) {
                    fputs("overlong record discarded\n", stderr);
                    used = 0; discarding = 1;
                } else line[used++] = chunk[i];
            }
        }
    }
}
