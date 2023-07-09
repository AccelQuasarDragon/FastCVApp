import sys

if hasattr(sys, "_MEIPASS"):
    # if file is frozen by pyinstaller add the MEIPASS folder to path:
    sys.path.append(sys._MEIPASS)
else:
    # if you're making your own app, you don't need this else block. This is just vanity code so I can run this from main FastCVApp folder or from the examples subfolder.
    # this example is importing from a higher level package if running from cmd: https://stackoverflow.com/a/41575089
    import os

    # add the right path depending on if you're running from examples or from main folder:
    if "examples" in os.getcwd().split(os.path.sep)[-1]:
        sys.path.append(
            ".."
        )  # when running from examples folder, append the upper level
    else:
        # assume they're in main folder trying `python examples/example_backgroundsubtraction.py`
        sys.path.append("../FastCVApp")  # when running from main folder

import FastCVApp

app = FastCVApp.FCVA()

# importing here means it's available to the subprocess as well. You can probably cut loading time by only loading mediapipe for the right subprocess.
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils  # Drawing helpers
mp_holistic = mp.solutions.holistic  # Mediapipe Solutions
import cv2


def open_mediapipe(*args):
    try:
        image = args[0]
        shared_analysis_dict = args[1]
        shared_metadata_dict = args[2]
        with mp_holistic.Holistic(
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        ) as holistic:
            while True:
                if "kivy_run_state" in shared_metadata_dict.keys():
                    if shared_metadata_dict["kivy_run_state"] == False:
                        break

                frame = shared_metadata_dict["latest_cap_frame"]
                # print("how long to read frame?", timef2 - timef1)# first frame takes a while and subsequent frames are fast: 0.9233419895172119 -> 0.006009101867675781

                # Recolor Feed
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False  # I have read that writable false/true this makes things faster for mediapipe holistic

                # Make Detections
                results = holistic.process(image)

                # Recolor image back to BGR for rendering
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                # 2. Right hand
                mp_drawing.draw_landmarks(
                    image,
                    results.right_hand_landmarks,
                    mp_holistic.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(
                        color=(80, 22, 10), thickness=2, circle_radius=4
                    ),
                    mp_drawing.DrawingSpec(
                        color=(80, 44, 121), thickness=2, circle_radius=2
                    ),
                )

                # 3. Left Hand
                mp_drawing.draw_landmarks(
                    image,
                    results.left_hand_landmarks,
                    mp_holistic.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(
                        color=(121, 22, 76), thickness=2, circle_radius=4
                    ),
                    mp_drawing.DrawingSpec(
                        color=(121, 44, 250), thickness=2, circle_radius=2
                    ),
                )

                # 4. Pose Detections6
                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_holistic.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(
                        color=(245, 117, 66), thickness=2, circle_radius=4
                    ),
                    mp_drawing.DrawingSpec(
                        color=(245, 66, 230), thickness=2, circle_radius=2
                    ),
                )

                shared_analysis_dict[1] = cv2.flip(image, 0)
    except Exception as e:
        print("open_mediapipe died!", e, flush=True)


app.appliedcv = open_mediapipe

if __name__ == "__main__":
    # / and \ works on windows, only / on mac tho
    app.source = "examples/creativecommonsmedia/Elephants Dream charstart2.webm"
    app.fps = 1 / 30
    app.title = "Mediapipe example by Pengindoramu"
    app.run()
