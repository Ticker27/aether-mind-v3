package com.samsung.android.service;

import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.PixelFormat;
import android.hardware.display.DisplayManager;
import android.hardware.display.VirtualDisplay;
import android.media.Image;
import android.media.ImageReader;
import android.media.projection.MediaProjection;
import android.media.projection.MediaProjectionManager;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.util.Log;

import java.nio.ByteBuffer;

/**
 * Aether Screen Capture Service
 * Implementation of the "Eyes" of AETHER SHOT
 */
public class ScreenCaptureService extends Service {
    private static final String TAG = "SAMSUNG_Svc_Capture";
    private static final int FPS = 20;
    private static final int WIDTH = 128; // Downscale for AI performance
    private static final int HEIGHT = 256;
    
    private MediaProjection mMediaProjection;
    private ImageReader mImageReader;
    private VirtualDisplay mVirtualDisplay;
    private Handler mHandler;
    private boolean mIsRunning = false;
    
    private AetherService mMainService;

    @Override
    public IBinder onBind(Intent intent) { return null; }

    public void setMainService(AetherService service) {
        this.mMainService = service;
    }

    public void startCapture(int resultCode, Intent data) {
        MediaProjectionManager manager = (MediaProjectionManager) getSystemService(Context.MEDIA_PROJECTION_SERVICE);
        mMediaProjection = manager.getMediaProjection(resultCode, data);
        
        mImageReader = ImageReader.newInstance(WIDTH, HEIGHT, PixelFormat.RGBA_8888, 2);
        mVirtualDisplay = mMediaProjection.createVirtualDisplay(
            "AetherCapture", WIDTH, HEIGHT, 1, 
            VirtualDisplay.FLAG_PUBLIC | VirtualDisplay.FLAG_SECURE,
            mImageReader.getSurface(), null, null
        );
        
        mHandler = new Handler(Looper.getMainLooper());
        mIsRunning = true;
        
        mImageReader.setOnImageAvailableListener(reader -> {
            if (!mIsRunning) return;
            
            Image image = reader.acquireLatestImage();
            if (image != null) {
                try {
                    ByteBuffer buffer = image.getPlane(0).getBuffer();
                    byte[] pixels = new byte[buffer.remaining()];
                    buffer.get(pixels);
                    
                    if (mMainService != null) {
                        mMainService.onFrameCaptured(pixels);
                    }
                } finally {
                    image.close();
                }
            }
        }, mHandler);
        
        Log.d(TAG, "Screen capture active at " + FPS + " FPS");
    }

    public void stopCapture() {
        mIsRunning = false;
        if (mVirtualDisplay != null) mVirtualDisplay.release();
        if (mMediaProjection != null) mMediaProjection.stop();
        if (mImageReader != null) mImageReader.close();
    }
}