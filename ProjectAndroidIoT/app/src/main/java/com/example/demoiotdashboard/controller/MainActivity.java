package com.example.demoiotdashboard.controller;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.SwitchCompat;
import android.graphics.Color;
import android.os.Bundle;
import android.util.Log;
import android.widget.CompoundButton;
import android.widget.TextView;

import com.example.demoiotdashboard.R;
import com.example.demoiotdashboard.mqtt.MQTTHelper;
import com.jjoe64.graphview.GraphView;
import com.jjoe64.graphview.series.DataPoint;
import com.jjoe64.graphview.series.LineGraphSeries;

import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttCallbackExtended;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;

import java.nio.charset.Charset;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.Date;


public class MainActivity extends AppCompatActivity {
    MQTTHelper mqttHelper;
    TextView txtTemp, txtHumi, txtAI;
    SwitchCompat buttonLED, buttonPUMP;
    GraphView temperatureGraph, humidityGraph;

    LineGraphSeries seriesTemperature = new LineGraphSeries<DataPoint>();
    LineGraphSeries seriesHumidity = new LineGraphSeries<DataPoint>();


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        txtTemp = findViewById(R.id.txtTemperature);
        txtHumi = findViewById(R.id.txtHumidity);
//        txtAI = findViewById(R.id.txtAI);
        buttonLED = findViewById(R.id.buttonLED);
        buttonPUMP = findViewById(R.id.buttonPUMP);

        temperatureGraph = (GraphView) findViewById(R.id.graph1);
        temperatureGraph.getGridLabelRenderer().setHorizontalLabelsVisible(false);
        temperatureGraph.getGridLabelRenderer().setGridColor(Color.WHITE);
        temperatureGraph.getGridLabelRenderer().setVerticalLabelsColor(Color.WHITE);
        temperatureGraph.getGridLabelRenderer().setHorizontalLabelsColor(Color.WHITE);
        temperatureGraph.getGridLabelRenderer().setVerticalLabelsColor(Color.WHITE);
        temperatureGraph.getGridLabelRenderer().setHorizontalLabelsColor(Color.WHITE);

        humidityGraph = (GraphView) findViewById(R.id.graph2);
        humidityGraph.getGridLabelRenderer().setHorizontalLabelsVisible(false);
        humidityGraph.getGridLabelRenderer().setGridColor(Color.WHITE);
        humidityGraph.getGridLabelRenderer().setVerticalLabelsColor(Color.WHITE);
        humidityGraph.getGridLabelRenderer().setHorizontalLabelsColor(Color.WHITE);
        humidityGraph.getGridLabelRenderer().setVerticalLabelsColor(Color.WHITE);
        humidityGraph.getGridLabelRenderer().setHorizontalLabelsColor(Color.WHITE);




        buttonLED.setOnCheckedChangeListener(
                new CompoundButton.OnCheckedChangeListener() {
                    @Override
                    public void onCheckedChanged(CompoundButton compoundButton,
                                                 boolean b) {
                        if (b == true) {
                            sendDataMQTT("minhtrung181/feeds/button", "ON");
                        } else {
                            sendDataMQTT("minhtrung181/feeds/button", "OFF");
                        }
                    }
                });

        buttonPUMP.setOnCheckedChangeListener(
                new CompoundButton.OnCheckedChangeListener() {
                    @Override
                    public void onCheckedChanged(CompoundButton compoundButton,
                                                 boolean b) {
                        if (b == true) {
                            sendDataMQTT("minhtrung181/feeds/button", "ON");
                        } else {
                            sendDataMQTT("minhtrung181/feeds/button", "OFF");
                        }
                    }
                });


        startMQTT();
    }

    public Date convertLocalDateTime (LocalDateTime y){
       Instant instant = y.toInstant(ZoneOffset.of("+07:00"));
       Date out = Date.from(instant);
        return out;
    }




    public void sendDataMQTT(String topic, String value){
        MqttMessage msg = new MqttMessage();
        msg.setId(1234);
        msg.setQos(0);
        msg.setRetained(false);

        byte[] b = value.getBytes(Charset.forName("UTF-8"));
        msg.setPayload(b);

        try {
            mqttHelper.mqttAndroidClient.publish(topic, msg);
        }catch (MqttException e){
        }
    }
    public void startMQTT(){
        mqttHelper = new MQTTHelper(this);
        mqttHelper.setCallback(new MqttCallbackExtended() {
            @Override
            public void connectComplete(boolean reconnect, String serverURI) {

            }

            @Override
            public void connectionLost(Throwable cause) {

            }

            @Override
            public void messageArrived(String topic, MqttMessage message) throws Exception {
                Log.d("TEST",topic+ "***" +message.toString());
                if (topic.contains("nhietdo")){
                    int x = Integer.parseInt(message.toString());
                    LocalDateTime time = LocalDateTime.now();
                    Date y = convertLocalDateTime(time);
                    seriesTemperature.appendData(new DataPoint(y,x), true, 5, true);
                    temperatureGraph.addSeries(seriesTemperature);
                    temperatureGraph.onDataChanged(true, true);
                    txtTemp.setText("Temperature: "  + message.toString() + "°C");
                }else if(topic.contains("haha")){
                    int x = Integer.parseInt(message.toString());
                    LocalDateTime time = LocalDateTime.now();
                    Date y = convertLocalDateTime(time);
                    seriesHumidity.appendData(new DataPoint(y,x), true, 5, true);
                    humidityGraph.addSeries(seriesHumidity);
                    humidityGraph.onDataChanged(true, true);
                    txtHumi.setText("Humidity: " + message.toString() + "%" );
                }else if(topic.contains("AI")){
                    txtAI.setText(message.toString());
                }else if(topic.contains("button")){
                    if (message.toString().equals("ON")){
                        buttonLED.setChecked(true);
                    }else{
                        buttonLED.setChecked(false);
                    }
                }else if(topic.contains("button")){
                    if(message.toString().equals("ON")) {
                        buttonPUMP.setChecked(true);
                    }else{
                        buttonPUMP.setChecked(false);
                    }
                }
            }

            @Override
            public void deliveryComplete(IMqttDeliveryToken token) {
            }
        });
    }

}