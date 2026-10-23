/* Trusted local benchmark launcher; never a peer executable service.
 * Linux/Android wait4 ru_maxrss is KiB for the waited-for child, not sampled PSS.
 */
#define _GNU_SOURCE
#include <errno.h>
#include <signal.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/resource.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

static volatile sig_atomic_t interrupted = 0;
static void stop_requested(int number) { interrupted = number; }
static double seconds_now(void) {
  struct timespec time;
  if (clock_gettime(CLOCK_MONOTONIC, &time) != 0) _exit(125);
  return time.tv_sec + time.tv_nsec / 1000000000.0;
}

int main(int argc, char **argv) {
  char *end = NULL;
  if (argc < 3) return 125;
  unsigned long timeout = strtoul(argv[1], &end, 10);
  if (!*argv[1] || *end || timeout < 1 || timeout > 1800) return 125;
  struct sigaction action = {0};
  action.sa_handler = stop_requested;
  sigemptyset(&action.sa_mask);
  if (sigaction(SIGTERM, &action, NULL) || sigaction(SIGINT, &action, NULL) ||
      sigaction(SIGHUP, &action, NULL) || sigaction(SIGPIPE, &action, NULL)) return 125;
  double started = seconds_now();
  pid_t child = fork();
  if (child < 0) return 125;
  if (child == 0) {
    signal(SIGTERM, SIG_DFL);
    signal(SIGINT, SIG_DFL);
    if (setpgid(0, 0) != 0) _exit(125);
    execv(argv[2], &argv[2]);
    _exit(127);
  }
  if (setpgid(child, child) != 0 && errno != EACCES && errno != ESRCH) {
    kill(child, SIGKILL);
    waitpid(child, NULL, 0);
    return 125;
  }
  int status = 0;
  struct rusage usage = {0};
  bool timed_out = false;
  double stopped = 0;
  for (;;) {
    pid_t result = wait4(child, &status, WNOHANG, &usage);
    if (result == child) break;
    if (result < 0 && errno != EINTR) return 125;
    double now = seconds_now();
    if (!stopped && (interrupted || now - started >= timeout)) {
      timed_out = !interrupted;
      stopped = now;
      kill(-child, SIGTERM);
    }
    if (stopped && now - stopped >= 0.5) kill(-child, SIGKILL);
    struct timespec pause = {0, 20000000};
    nanosleep(&pause, NULL);
  }
  /* Descendants in this runner's own group must not outlive the trial. */
  kill(-child, SIGKILL);
  int code = WIFEXITED(status) ? WEXITSTATUS(status) : 128 + WTERMSIG(status);
  printf("\nP2PLLMResource {\"exit_code\":%d,\"timed_out\":%s,"
         "\"interrupted\":%s,\"peak_rss_kib\":%ld,\"wall_ms\":%.3f}\n",
         code, timed_out ? "true" : "false", interrupted ? "true" : "false",
         usage.ru_maxrss, (seconds_now() - started) * 1000);
  fflush(stdout);
  return timed_out ? 124 : (interrupted ? 130 : code);
}
