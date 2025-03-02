from flask import Flask, jsonify
import cv2
import mediapipe as mp

app = Flask(__name__)
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
cap = cv2.VideoCapture(0)

@app.route('/pose', methods=['GET'])
def detect_pose():
    ret, frame = cap.read()
    if not ret:
        return jsonify({'error': 'Failed to capture image'})

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    keypoints = {}
    if results.pose_landmarks:
        for i, landmark in enumerate(results.pose_landmarks.landmark):
            keypoints[i] = {'x': landmark.x, 'y': landmark.y}

    left_wrist = keypoints.get(15, {})
    right_wrist = keypoints.get(16, {})
    left_elbow = keypoints.get(13, {})
    right_elbow = keypoints.get(14, {})
    left_shoulder = keypoints.get(11, {})
    right_shoulder = keypoints.get(12, {})

    # Move the collar slightly down (10% lower than the average shoulder height)
    neck_x = (left_shoulder.get('x', 0) + right_shoulder.get('x', 0)) / 2
    neck_y = (left_shoulder.get('y', 0) + right_shoulder.get('y', 0)) / 2 + 0.05

    return jsonify({
        'keypoints': keypoints,
        'neck': {'x': neck_x, 'y': neck_y},
        'left_wrist': left_wrist,
        'right_wrist': right_wrist,
        'left_elbow': left_elbow,
        'right_elbow': right_elbow
    })

if __name__ == '__main__':
    app.run(debug=True)
