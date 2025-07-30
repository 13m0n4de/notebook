# 第 5 章 插叙：进程 API

这章只是介绍了一些有关进程的 API。

| 系统调用 | 功能               | 返回值                                                        | 备注                                                                                                                                                                                                                             |
| :------- | :----------------- | :------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| fork     | 创建子进程         | 在父进程中返回子进程的 PID，子进程中返回 `0`，失败时返回 `-1` | 子进程会复制一份父进程的内存内容，但它们在不同的内存空间，运行 `mmap` 等不会互相影响                                                                                                                                             |
| wait     | 等待子进程运行完毕 | 成功时返回结束的子进程 PID，失败时返回 `-1`                   | 调用 `wait()` 等于调用 `waitpid(-1, &wstatus, 0)`，会等待任意一个子进程结束                                                                                                                                                      |
| exec     | 执行新的程序       | 只有发生错误才会返回，返回 `-1`                               | 它实际做的是使用新的进程映像替换当前进程映像，从可执行程序中加载代码和静态数据，并用它覆写自己的代码段（以及静态数据），堆、栈及其他内存空间也会被重新初始化。所以 `exec()` 等函数执行成功后没法返回，因为原有的程序已经被替换了 |

作业中会用到更多。

手册：[Linux man pages online](https://man7.org/linux/man-pages/)

## 作业

!!! question

    1．编写一个调用 fork()的程序。在调用 fork()之前，让主进程访问一个变量（例如 x）并将其值设置为某个值（例如 100）。子进程中的变量有什么值？当子进程和父进程都改变 x的值，变量会发生什么？

!!! note "Answer"

    ```c title='q1.c'
    #include <assert.h>
    #include <stdio.h>
    #include <unistd.h>

    int main() {
        int x;
        x = 100;

        pid_t rc = fork();
        assert(rc >= 0);

        if (rc == 0) {
            for (size_t i = 0; i < 5; ++i) {
                printf("Child(%d):\tx = %d\n", getpid(), x);
                x += 100;
                printf("Child(%d):\tx += 100\n", getpid());
                sleep(1);
            }
        } else {
            for (size_t i = 0; i < 5; ++i) {
                printf("Parent(%d):\tx = %d\n", getpid(), x);
                x += 70;
                printf("Parent(%d):\tx += 70\n", getpid());
                sleep(1);
            }
        }

        return 0;
    }
    ```

    ```title='cc q1.c -o q1 -Wall -Wextra -pedantic && ./q1'
    Parent(13645):  x = 100
    Parent(13645):  x += 70
    Child(13646):   x = 100
    Child(13646):   x += 100
    Parent(13645):  x = 170
    Parent(13645):  x += 70
    Child(13646):   x = 200
    Child(13646):   x += 100
    Parent(13645):  x = 240
    Parent(13645):  x += 70
    Child(13646):   x = 300
    Child(13646):   x += 100
    Child(13646):   x = 400
    Parent(13645):  x = 310
    Child(13646):   x += 100
    Parent(13645):  x += 70
    Child(13646):   x = 500
    Parent(13645):  x = 380
    Child(13646):   x += 100
    Parent(13645):  x += 70
    ```

    子进程获得了父进程数据段、堆和栈的副本，意味着子进程中的 `x` 会有与父进程相同的初始值 `100`，但父进程和子进程中的 `x` 是彼此独立的，互不影响。

!!! question

    2．编写一个打开文件的程序（使用 open()系统调用），然后调用 fork()创建一个新进程。子进程和父进程都可以访问 open()返回的文件描述符吗？当它们并发（即同时）写入文件时，会发生什么？

!!! note "Answer"

    ```c title='q2.c'
    #include <assert.h>
    #include <fcntl.h>
    #include <unistd.h>

    int main() {
        pid_t rc = fork();
        assert(rc >= 0);

        int fd = open("/tmp/testfile", O_WRONLY | O_CREAT | O_APPEND, S_IRWXU);
        assert(fd > -1);

        if (rc == 0) {
            assert(fcntl(fd, F_GETFL, 0) != -1);
            assert(write(fd, "bbbbbbbb", 8) != -1);
        } else {
            assert(fcntl(fd, F_GETFL, 0) != -1);
            assert(write(fd, "aaaaaaaa", 8) != -1);
        }

        close(fd);
        return 0;
    }
    ```

    ```title='cc q2.c -o q2 -Wall -Wextra -pedantic && ./q2 && cat /tmp/testfile'
    aaaaaaaabbbbbbbb
    ```

    文件描述符在子进程和父进程中都可以使用，且关闭描述符互不影响。<br>
    同时写入的话，好像没问题？数据量小于 `PIPE_BUF` 时 `write` 看起来像原子的。

!!! question

    3．使用 fork()编写另一个程序。子进程应打印“hello”，父进程应打印“goodbye”。你应该尝试确保子进程始终先打印。你能否不在父进程调用 wait()而做到这一点呢？

!!! note "Answer"

    ```c title='q3.c'
    #include <assert.h>
    #include <stdio.h>
    #include <unistd.h>

    int main() {
        pid_t rc = vfork();
        assert(rc >= 0);

        if (rc == 0) {
            printf("hello");
        } else {
            printf("goodbye");
        }

        return 0;
    }
    ```

    ```title='cc q3.c -o q3 -Wall -Wextra -pedantic && ./q3'
    hellogoodbye
    ```

    `vfork` 与 `fork` 的区别是，它会阻塞父进程直到子进程退出，而且不会完全复制父进程的地址空间。

!!! question

    4．编写一个调用 fork()的程序，然后调用某种形式的 exec()来运行程序/bin/ls。看看是否可以尝试 exec()的所有变体，包括 execl()、execle()、execlp()、execv()、execvp()和 execvP()。为什么同样的基本调用会有这么多变种？

!!! note ""

    变种很多，命名规则都是 `exec` + 后缀。<br>

    - `l` 代表 list，以可变参数的形式传递命令行参数，需要 `#!c (char*)NULL` 结尾
    - `v` 代表 vector，以 `#!c char *argv[]` 的形式传递命令行参数，需要 `#!c NULL` 结尾
    - `e` 代表 environment，支持传递环境变量，需要 `#!c NULL` 结尾
    - `p` 代表 path，在 PATH 环境变量中搜索可执行文件，而不需要提供完整路径

    例如 `execve` 需要传递可执行文件的绝对路径，并使用数组传递命令行参数，且可以传递环境变量。

    这些变种提供了不同级别的灵活性和控制，可以根据实际情况选择合适的函数。

    ```c
    #include <assert.h>
    #include <stdio.h>
    #include <sys/wait.h>
    #include <unistd.h>

    int main() {
        for (int i = 0; i < 5; i++) {
            pid_t pid = fork();
            assert(pid >= 0);

            if (pid == 0) {
                char* args[] = {"ls", "-l", NULL};
                char* env[] = {NULL};

                switch (i) {
                    case 0:
                        printf("execl:\n");
                        execl("/bin/ls", "ls", "-l", (char*)NULL);
                        break;
                    case 1:
                        printf("execle:\n");
                        execle("/bin/ls", "ls", "-l", (char*)NULL, env);
                        break;
                    case 2:
                        printf("execlp:\n");
                        execlp("ls", "ls", "-l", (char*)NULL);
                        break;
                    case 3:
                        printf("execv:\n");
                        execv("/bin/ls", args);
                        break;
                    case 4:
                        printf("execvp:\n");
                        execvp("ls", args);
                        break;
                }

                perror("exec");
                return 1;
            } else {
                wait(NULL);
            }
        }

        return 0;
    }
    ```

!!! question

    5．现在编写一个程序，在父进程中使用 wait()，等待子进程完成。wait()返回什么？如果你在子进程中使用 wait()会发生什么？

!!! note "Answer"

    ```c title='q5.c'
    #include <assert.h>
    #include <stdio.h>
    #include <sys/wait.h>
    #include <unistd.h>

    int main() {
        pid_t pid = fork();
        assert(pid >= 0);

        if (pid == 0) {
            printf("child PID: %d\n", getpid());
            return wait(NULL);
        } else {
            int status;
            pid_t child_pid = wait(&status);
            assert(child_pid >= 0);

            if (WIFEXITED(status)) {
                printf("normal termination of child (%d), exit status: %d\n",
                       child_pid, WEXITSTATUS(status));
            }
            return 0;
        }
    }
    ```

    ```title='cc q5.c -o q5 -Wall -Wextra -pedantic && ./q5'
    child PID: 46008
    normal termination of child (46008), exit status: 255
    ```

    父进程中使用 `wait()` 返回已停止子进程的 PID，还会顺带设置状态信息。<br>
    如果在子进程（没有子进程的进程）中使用 `wait()` 会出错返回 `-1`。

!!! question

    6．对前一个程序稍作修改，这次使用 waitpid()而不是 wait()。什么时候 waitpid()会有用？

!!! note "Answer"

    ```c title='p6.c'
    #include <assert.h>
    #include <stdio.h>
    #include <sys/wait.h>
    #include <unistd.h>

    int main() {
        pid_t pid = fork();
        assert(pid >= 0);

        if (pid == 0) {
            printf("child PID: %d\n", getpid());
            return wait(NULL);
        } else {
            int status;
            pid_t child_pid = waitpid(pid, &status, WUNTRACED);
            assert(child_pid >= 0);

            if (WIFEXITED(status)) {
                printf("normal termination of child (%d), exit status: %d\n",
                       child_pid, WEXITSTATUS(status));
            }
            return 0;
        }
    }
    ```

    ```title='cc q6.c -o q6 -Wall -Wextra -pedantic && ./q6'
    child PID: 46011
    normal termination of child (46011), exit status: 255
    ```

    `waitpid` 可以等待某个指定 PID 的子进程，而且拥有更灵活的选项参数。

!!! question

    7．编写一个创建子进程的程序，然后在子进程中关闭标准输出（STDOUT_FILENO）。如果子进程在关闭描述符后调用 printf()打印输出，会发生什么？

!!! note "Answer"

    ```c title='q7.c'
    #include <assert.h>
    #include <stdio.h>
    #include <sys/wait.h>
    #include <unistd.h>

    int main() {
        pid_t pid = fork();
        assert(pid >= 0);

        if (pid == 0) {
            close(STDOUT_FILENO);
            printf("child PID: %d\n", getpid());
        } else {
            int status;
            pid_t child_pid = wait(&status);
            assert(child_pid >= 0);

            if (WIFEXITED(status)) {
                printf("normal termination of child (%d), exit status: %d\n",
                       child_pid, WEXITSTATUS(status));
            }
        }
        return 0;
    }
    ```

    ```title='cc q7.c -o q7 -Wall -Wextra -pedantic && ./q7'
    normal termination of child (47157), exit status: 0
    ```

    同之前的例子，关闭文件描述符只影响本进程。

!!! question

    8．编写一个程序，创建两个子进程，并使用 pipe()系统调用，将一个子进程的标准输出连接到另一个子进程的标准输入。

!!! note "Answer"

    ```c title='q8.c'
    #include <assert.h>
    #include <stdio.h>
    #include <sys/wait.h>
    #include <unistd.h>

    int main() {
        int fd[2];
        assert(pipe(fd) != -1);

        char buf[25] = {0};
        pid_t child_process[2];

        for (int i = 0; i < 2; ++i) {
            pid_t pid = fork();
            assert(pid >= 0);

            if (pid == 0) {
                switch (i) {
                    case 0:
                        dup2(fd[1], STDOUT_FILENO);
                        printf("Message from child %d\n", getpid());
                        fflush(stdout);
                        break;
                    case 1:
                        dup2(fd[0], STDIN_FILENO);
                        fgets(buf, 25, stdin);
                        printf("Received message: %s", buf);
                        break;
                }
                return 0;
            } else {
                child_process[i] = pid;
            }
        }

        waitpid(child_process[0], NULL, 0);
        waitpid(child_process[1], NULL, 0);

        return 0;
    }
    ```

    ```title='cc q8.c -o q8 -Wall -Wextra -pedantic && ./q8'
    Received message: Message from child 5786
    ```
