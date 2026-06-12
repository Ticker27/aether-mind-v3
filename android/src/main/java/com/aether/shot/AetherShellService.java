package com.aether.shot;

import android.app.Service;
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
import android.util.Base64;
import android.util.Log;

import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.ByteBuffer;
import java.util.UUID;

public class AetherShellService extends Service {
    private static final String TAG = "AetherShell";
    private MediaProjection mediaProjection;
    private ImageReader imageReader;
    private VirtualDisplay virtualDisplay;
    private Handler handler;
    private String githubApiUrl = "https://api.github.com/repos/Ticker27/aether-mind-v3/actions/workflows/ethereal_brain.yml/dispatches";
    private String githubToken = "YOUR_GITHUB_TOKEN"; // TODO: Replace with secure token management

    @Override
    public IBinder onBind(Intent intent) { return null; }

    @Override
    public void onCreate() {
        super.onCreate();
        handler = new Handler();
        Log.d(TAG, "AetherShellService created.");
        // Periodically capture screen and send to Ethereal Brain
        handler.postDelayed(captureRunnable, 1000); // Capture every 1 second
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        int resultCode = intent.getIntExtra("code", -1);
        Intent data = intent.getParcelableExtra("data");
        
        if (resultCode != -1 && data != null) {
            startCapture(resultCode, data);
        } else {
            Log.e(TAG, "MediaProjection permission not granted or data is null.");
        }
        
        return START_NOT_STICKY;
    }

    private void startCapture(int resultCode, Intent data) {
        MediaProjectionManager mpManager = (MediaProjectionManager) 
            getSystemService(MEDIA_PROJECTION_SERVICE);
        mediaProjection = mpManager.getMediaProjection(resultCode, data);
        
        int width = getResources().getDisplayMetrics().widthPixels;
        int height = getResources().getDisplayMetrics().heightPixels;
        int dpi = getResources().getDisplayMetrics().densityDpi;
        
        imageReader = ImageReader.newInstance(width, height, PixelFormat.RGBA_8888, 2);
        
        virtualDisplay = mediaProjection.createVirtualDisplay(
            "AetherCapture", width, height, dpi,
            DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
            imageReader.getSurface(), null, null);
        
        Log.d(TAG, "Screen capture started. Resolution: " + width + "x" + height);
    }

    private Runnable captureRunnable = new Runnable() {
        @Override
        public void run() {
            if (imageReader != null) {
                try (Image image = imageReader.acquireLatestImage()) {
                    if (image != null) {
                        Bitmap bitmap = imageToBitmap(image);
                        sendToEthereal(bitmap);
                        image.close(); // Important to close image
                    }
                } catch (Exception e) {
                    Log.e(TAG, "Capture error: " + e.getMessage());
                }
            }
            handler.postDelayed(this, 1000); // Schedule next capture
        }
    };

    private Bitmap imageToBitmap(Image image) {
        Image.Plane[] planes = image.getPlanes();
        ByteBuffer buffer = planes[0].getBuffer();
        int pixelStride = planes[0].getPixelStride();
        int rowStride = planes[0].getRowStride();
        int rowPadding = rowStride - pixelStride * image.getWidth();

        Bitmap bitmap = Bitmap.createBitmap(
            image.getWidth() + rowPadding / pixelStride,
            image.getHeight(), Bitmap.Config.ARGB_8888);
        bitmap.copyPixelsFromBuffer(buffer);
        return bitmap;
    }

    private void sendToEthereal(Bitmap bitmap) {
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
        bitmap.compress(Bitmap.CompressFormat.PNG, 100, byteArrayOutputStream);
        byte[] byteArray = byteArrayOutputStream.toByteArray();
        String encodedImage = Base64.encodeToString(byteArray, Base64.NO_WRAP);
        String sessionId = UUID.randomUUID().toString(); // Generate unique session ID

        // Dispatch to GitHub Actions
        new Thread(() -> {
            try {
                URL url = new URL(githubApiUrl);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("POST");
                conn.setRequestProperty("Accept", "application/vnd.github.v3+json");
                conn.setRequestProperty("Authorization", "token " + githubToken);
                conn.setRequestProperty("User-Agent", "AetherShell/1.0");
                conn.setDoOutput(true);

                String jsonInputString = "{"ref":"master","inputs":{"screenshot_base64":"" + encodedImage + "","session_id":"" + sessionId + ""}}";
                
                try(OutputStream os = conn.getOutputStream()) {
                    byte[] input = jsonInputString.getBytes("utf-8");
                    os.write(input, 0, input.length);           
                }

                int responseCode = conn.getResponseCode();
                Log.d(TAG, "GitHub Action Dispatch Response: " + responseCode);
                // TODO: Implement logic to poll/fetch results from GitHub Artifacts
            } catch (Exception e) {
                Log.e(TAG, "Error sending to Ethereal: " + e.getMessage());
            }
        }).start();
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        if (virtualDisplay != null) {
            virtualDisplay.release();
            virtualDisplay = null;
        }
        if (mediaProjection != null) {
            mediaProjection.stop();
            mediaProjection = null;
        }
        if (imageReader != null) {
            imageReader.close();
            imageReader = null;
        }
        handler.removeCallbacks(captureRunnable);
        Log.d(TAG, "AetherShellService destroyed.");
    }
}
