#reference: https://github.com/google/mediapipe/issues/2323
import mediapipe as mp
from multiprocessing import Pool, cpu_count
import numpy as np


N = 100_000  
# Number of "images" each process will run for.
# Pick a large number, so it runs until the crash.


def process_landmarks(id):
    with mp.solutions.face_mesh.FaceMesh(
        static_image_mode=True, max_num_faces=1, min_detection_confidence=0.75
    ) as face_mesh:
        fake_image = np.random.randint(0, 255, [500, 500, 3], np.uint8)
        for i in range(N):
            landmarks = face_mesh.process(fake_image)
            print(f"Process {id}: Completed {i} images, {100 * i / N:.5}%")
        print(f"Process {id}: finished.")


def main():
    num_workers = cpu_count()  # 12 for me
    assert num_workers > 1, "Need more than 1 worker to reproduce the bug (I think)"
    pool = Pool(processes=num_workers)
    pool.map(process_landmarks, [i for i in range(num_workers)])


if __name__ == "__main__":
    main()