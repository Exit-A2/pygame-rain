# https://qiita.com/h_sakurai/items/3e8d157954180c5b4610

import ffmpeg, pygame

process = None


def key(w, h, fps):
    global process, pw, ph
    if process:
        return stop()
    pw = w
    ph = h
    process = (
        ffmpeg.input(
            "pipe:", format="rawvideo", pix_fmt="rgb24", s="{}x{}".format(pw, ph), r=fps
        )
        .output("out.mkv", preset="ultrafast", qp=0)
        .overwrite_output()
        .run_async(pipe_stdin=True)
    )


def stop():
    if process:
        process.stdin.close()
        process.wait()


def draw(g):
    if process:
        g = pygame.transform.scale(g, (pw, ph))
        g = pygame.surfarray.pixels3d(g).swapaxes(0, 1)
        g = g.tobytes()
        process.stdin.write(g)
