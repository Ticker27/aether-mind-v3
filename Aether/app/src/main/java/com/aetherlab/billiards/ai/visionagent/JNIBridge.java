package com.aetherlab.billiards.ai.visionagent;

import android.media.Image;
import android.media.ImageReader;
import android.media.projection.MediaProjection;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.Surface;

public class JNIBridge {
    private static final String TAG = "AetherJNI";
    private MediaProjection mediaProjection;
    private ImageReader imageReader;
    private volatile boolean isRunning = false;

    private static native void nativeInit(String modelPath, int width, int height);
    private static native void nativeProcessFrame(long timestamp, int width, int height, byte[] rgbaData);
    private static native void nativeDestroy();

    public void startCapture(MediaProjection mp, int width, int height, int dpi) {
        this.mediaProjection = mp;
        String modelPath = getExternalFilesDir(null).getAbsolutePath() + "/models/";
        nativeInit(modelPath, width, height);

        imageReader = ImageReader.newInstance(width, height, android.graphics.PixelFormat.RGBA_8888, 4);
        imageReader.setOnImageAvailableListener(reader -> {
            if (!isRunning) return;
            Image image = reader.acquireLatestImage();
            if (image != null) {
                Image.Plane plane = image.getPlanes()[0];
                java.nio.ByteBuffer buffer = plane.getBuffer();
                byte[] rgbaData = new byte[buffer.remaining()];
                buffer.get(rgbaData);
                nativeProcessFrame(image.getTimestamp(), width, height, rgbaData);
                image.close();
            }
        }, new Handler(Looper.getMainLooper()));

        Surface surface = imageReader.getSurface();
        mp.createVirtualDisplay("AetherCapture", width, height, dpi,
                android.hardware.display.DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                surface, null, null);
        isRunning = true;
        Log.i(TAG, "Screen capture started");
    }

    public void stopCapture() {
        isRunning = false;
        nativeDestroy();
        if (mediaProjection != null) {
            mediaProjection.stop();
            mediaProjection = null;
        }
        if (imageReader != null) {
            imageReader.close();
            imageReader = null;
        }
    }

    public static boolean onAIShoot(float[] pathX, float[] pathY, long[] timestampsMs) {
        Log.i(TAG, "Executing AI shot with " + pathX.length + " points");
        return TouchService.performDrag(pathX, pathY, timestampsMs);
    }
}
