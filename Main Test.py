import argparse
from pathlib import Path
import cv2
import mediapipe as mp
import time


def get_backends():
    # On Windows, DirectShow is often the most reliable webcam backend.
    return [cv2.CAP_DSHOW, cv2.CAP_MSMF, None]


def backend_name(backend):
    if backend == cv2.CAP_DSHOW:
        return 'DSHOW'
    if backend == cv2.CAP_MSMF:
        return 'MSMF'
    return 'default'


def verify_capture(cap, attempts=3):
    if cap is None or not cap.isOpened():
        return False
    for _ in range(attempts):
        success, frame = cap.read()
        if success and frame is not None and frame.size > 0:
            return True
    return False


def open_camera(max_index=2):
    for backend in get_backends():
        backend_name_str = backend_name(backend)
        for idx in range(max_index):
            cap = cv2.VideoCapture(idx) if backend is None else cv2.VideoCapture(idx, backend)
            if cap.isOpened() and verify_capture(cap):
                print(f'Opened camera index {idx} using backend {backend_name_str}')
                return cap
            print(f'Failed to open usable camera at index {idx} with backend {backend_name_str}')
            cap.release()
    return None


def open_source(source):
    if source is None:
        return open_camera()

    if source.isdigit():
        idx = int(source)
        for backend in get_backends():
            backend_name_str = backend_name(backend)
            cap = cv2.VideoCapture(idx) if backend is None else cv2.VideoCapture(idx, backend)
            if cap.isOpened() and verify_capture(cap):
                print(f'Opened camera index {idx} using backend {backend_name_str}')
                return cap
            print(f'Failed to open usable camera at index {idx} with backend {backend_name_str}')
            cap.release()
        return None

    path = Path(source)
    if path.exists():
        cap = cv2.VideoCapture(str(path))
        if cap.isOpened():
            print(f'Opened video file: {path}')
            return cap
        cap.release()
    return None


def parse_args():
    parser = argparse.ArgumentParser(description='Live 468 Face Landmarks with MediaPipe')
    parser.add_argument(
        '--source',
        type=str,
        default=None,
        help='Camera index or video file path. If omitted, the script tries available webcams.',
    )
    return parser.parse_args()


def main():
    args = parse_args()

    cap = open_source(args.source)
    if cap is None:
        raise IOError(
            'Cannot open the selected source. '
            'If you want a webcam, make sure it is connected and not used by another app. '
            'To use a video file, pass --source path/to/video.mp4.'
        )

    mp_draw: object = mp.solutions.drawing_utils
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=2,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    draw_spec = mp_draw.DrawingSpec(thickness=1, circle_radius=1, color=(0, 255, 0))
    connection_spec = mp_draw.DrawingSpec(thickness=1, circle_radius=1, color=(255, 0, 0))

    window_name = 'Live 468 Face Landmarks'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 960, 720)
    cv2.moveWindow(window_name, 100, 100)
    print(f'Preparing window: {window_name}')
    window_check_done = False
    p_time = 0

    while True:
        success, img = cap.read()
        if not success:
            print('Stream ended or frame not available.')
            break

        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(img_rgb)

        face_count = 0
        if results.multi_face_landmarks:
            face_count = len(results.multi_face_landmarks)
            for face_landmarks in results.multi_face_landmarks:
                mp_draw.draw_landmarks(
                    img,
                    face_landmarks,
                    mp_face_mesh.FACE_CONNECTIONS,
                    landmark_drawing_spec=draw_spec,
                    connection_drawing_spec=connection_spec,
                )

        c_time = time.time()
        fps = 1 / (c_time - p_time) if c_time != p_time else 0
        p_time = c_time

        cv2.putText(
            img,
            f'Faces: {face_count}',
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        cv2.putText(
            img,
            f'FPS: {int(fps)}',
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        cv2.putText(
            img,
            'Press Q to quit',
            (20, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.imshow(window_name, img)
        if not window_check_done:
            visible = cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE)
            print('Window visibility property:', visible)
            window_check_done = True

        key = cv2.waitKey(1)
        if key != -1:
            print('waitKey returned', key)
        if key != -1 and key & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
