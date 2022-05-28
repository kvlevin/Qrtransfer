package example.zxing;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.Settings;
import android.text.method.ScrollingMovementMethod;
import android.view.KeyEvent;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import com.google.zxing.BarcodeFormat;
import com.google.zxing.ResultPoint;
import com.google.zxing.client.android.BeepManager;
import com.journeyapps.barcodescanner.BarcodeCallback;
import com.journeyapps.barcodescanner.BarcodeResult;
import com.journeyapps.barcodescanner.DecoratedBarcodeView;
import com.journeyapps.barcodescanner.DefaultDecoderFactory;

import androidx.appcompat.app.AppCompatActivity;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Arrays;
import java.util.Collection;
import java.util.List;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;


public class MainActivity extends AppCompatActivity {
    private DecoratedBarcodeView barcodeView;
    private BeepManager beepManager;

    private boolean started=false;
    private String fileName="";
    private int headLength;
    private int receivedFrame=0;
    private int chunkSize;
    private int totalFrame;
    private int fileSize;
    private FileOutputStream mFile;

    private TextView progress_state;

    LinkedBlockingQueue<BarcodeResult> queue;
    private boolean running =false;


    private void log(String msg){
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                progress_state.append(msg);
                int offset=progress_state.getLineCount()*progress_state.getLineHeight();
                if(offset>progress_state.getHeight()){
                    progress_state.scrollTo(0,offset-progress_state.getHeight());
                }

            }
        });
    }


    private File createLocalFile(){
        File picFile = getExternalFilesDir("");
        if(!picFile.exists()){
            try {
                picFile.createNewFile();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        return picFile;
    }

    private BarcodeCallback callback = new BarcodeCallback() {


        @Override
        public void barcodeResult(BarcodeResult result) {


                queue.offer(result);



            //lastText = result.getText();
           // barcodeView.setStatusText(result.getText());

          //  beepManager.playBeepSoundAndVibrate();

            //Added preview of scanned barcode

            //imageView.setImageBitmap(result.getBitmapWithResultPoints(Color.YELLOW));
        }

        @Override
        public void possibleResultPoints(List<ResultPoint> resultPoints) {
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        setContentView(R.layout.continuous_scan);

        barcodeView = findViewById(R.id.barcode_scanner);
        progress_state = findViewById(R.id.progress_state);
        progress_state.setMovementMethod(ScrollingMovementMethod.getInstance());
        Collection<BarcodeFormat> formats = Arrays.asList(BarcodeFormat.QR_CODE);
        barcodeView.getBarcodeView().setDecoderFactory(new DefaultDecoderFactory(formats));
        barcodeView.initializeFromIntent(getIntent());
        barcodeView.decodeContinuous(callback);
       // beepManager = new BeepManager(this);
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            // 适配android11读写权限
            if (Environment.isExternalStorageManager()) {
                //已获取android读写权限
            } else {
                Intent intent = new Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION);
                intent.setData(Uri.parse("package:" + getPackageName()));

                startActivityForResult(intent, 0,null);
//                ActivityCompat.requestPermissions(this,
//                        new String[]{Manifest.permission.CAMERA,
//                                Manifest.permission.WRITE_EXTERNAL_STORAGE,
//                                Manifest.permission.READ_EXTERNAL_STORAGE},1);
            }
        }

        queue=new LinkedBlockingQueue<BarcodeResult>();
        running =true;
        new Thread(new Runnable() {
            @Override
            public void run() {
                while (running) {
                    try {
                        BarcodeResult result = queue.poll(1, TimeUnit.SECONDS);
                        if(result==null)continue;
                        if(started){
                            byte[] raw = result.getRawBytes();
                            int localFrame=0;
                            localFrame+= raw[0];
                            localFrame<<=8;
                            localFrame+= raw[1];
                            localFrame<<=8;
                            localFrame+= raw[2];
                            localFrame<<=8;
                            localFrame+= raw[3];
                            log("\nreceived frame:"+localFrame);
                            if(localFrame==receivedFrame+1){
                                if(localFrame==1){
                                    File parent=createLocalFile();

                                    File file = new File(parent,fileName);
                                    //判断文件是否存在，存在就删除
                                    if (file.exists()){
                                        file.delete();
                                    }
                                    try {
                                        //创建文件
                                        file.createNewFile();
                                        mFile= new FileOutputStream(file);

                                    } catch ( Exception e) {
                                        e.printStackTrace();
                                    }
                                }
                                    try {
                                        mFile.write(raw,4,raw.length-4);
                                        if(localFrame==totalFrame) {
                                            mFile.flush();
                                            mFile.close();
                                        }

                                        log("\nwrite frame:"+localFrame);
                                        receivedFrame=localFrame;
                                    } catch (IOException e) {
                                        e.printStackTrace();
                                    }



                            }else if((receivedFrame>0&&(localFrame-receivedFrame)>1)||(receivedFrame==0&&localFrame<100)){
                                log("Tranfer Fail!,Please Seek To "+receivedFrame+" And Start!");
                                runOnUiThread(new Runnable() {
                                    @Override
                                    public void run() {
                                        Toast.makeText(MainActivity.this,"Tranfer Fail!,Please Seek To "+receivedFrame+" And Start!",Toast.LENGTH_LONG).show();


                                    }
                                });
                            }
                        }else{
                            String text=result.getText();
                            if(text != null ) {
                                try {
                                    JSONObject meta=new JSONObject(text);
                                    if(!fileName.equals(meta.getString("fileName")))
                                        progress_state.append(text);
                                    fileName=meta.getString("fileName");
                                    headLength=meta.getInt("headLength");
                                    chunkSize=meta.getInt("chunkSize");
                                    totalFrame=meta.getInt("totalFrame");
                                    fileSize=meta.getInt("fileSize");
                                    receivedFrame=0;
                                    started=true;
                                } catch (JSONException e) {
                                }


                            }
                        }


                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }



            }
        }).start();
    }

    @Override
    protected void onPause() {
        super.onPause();
        this.stop(null);
        running=false;
    }

    public void stop(View view) {
        barcodeView.pause();
    }

    public void start(View view) {
        barcodeView.resume();
    }



    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        return barcodeView.onKeyDown(keyCode, event) || super.onKeyDown(keyCode, event);
    }
}
