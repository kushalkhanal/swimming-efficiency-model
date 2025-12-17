# MediaPipe Installation Note

## Python 3.13 Compatibility Issue

MediaPipe does not currently have pre-built wheels for Python 3.13. The project code is designed to handle this gracefully - MediaPipe is imported with a try/except block and will raise a clear error message if pose estimation is attempted without MediaPipe installed.

## Options:

1. **Use Python 3.11 or 3.12** (Recommended)
   - Create a new virtual environment with Python 3.11 or 3.12
   - MediaPipe will install successfully on these versions
   - Example: `python3.11 -m venv .venv311`

2. **Wait for MediaPipe Python 3.13 Support**
   - MediaPipe team is working on Python 3.13 support
   - Check: https://pypi.org/project/mediapipe/

3. **Use Alternative Pose Estimation**
   - The code structure allows for alternative pose estimation libraries
   - You can modify `backend/app/services/pose_estimation.py` to use other libraries like:
     - OpenPose (requires separate installation)
     - MMPose (from OpenMMLab)
     - Custom pose estimation models

## Current Status

- ✅ All other dependencies installed successfully
- ✅ Backend server can start (will fail only when pose estimation is called)
- ✅ Frontend dependencies installed
- ⚠️ MediaPipe pose estimation will not work until MediaPipe is installed

## Testing Without MediaPipe

You can test the rest of the application (video upload, detection, etc.) even without MediaPipe. The pose estimation step will fail with a clear error message when attempted.


