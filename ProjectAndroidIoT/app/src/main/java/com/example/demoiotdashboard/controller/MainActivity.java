package com.example.demoiotdashboard.controller;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.SwitchCompat;
import android.graphics.Color;
import android.os.Bundle;
import android.util.Log;
import android.widget.CompoundButton;
import android.widget.ScrollView;
import android.widget.TextView;

import com.example.demoiotdashboard.R;

import com.example.demoiotdashboard.alert.Alerts;
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
    TextView txtAirTemp, txtAirHumidity, txtAI, txtSoilTemperature, txtSoilHumidity;
    SwitchCompat buttonLED, buttonPUMP;
    GraphView airHumidityGraph, airTemperatureGraph, soilTemperature, soilHumidity;

    Alerts alertDialog;

    LineGraphSeries seriesAirTemperature = new LineGraphSeries<DataPoint>();
    LineGraphSeries seriesAirHumidity = new LineGraphSeries<DataPoint>();
    LineGraphSeries seriesSoilHumidity = new LineGraphSeries<DataPoint>();
    LineGraphSeries seriesSoilTemperature = new LineGraphSeries<DataPoint>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        txtAirTemp = findViewById(R.id.txtAirTemperature);
        txtAirHumidity = findViewById(R.id.txtAirHumidity);
        txtSoilTemperature = findViewById(R.id.txtSoilTemperature);
        txtSoilHumidity = findViewById(R.id.txtSoilHumidity);

//        txtAI = findViewById(R.id.txtAI);
        buttonLED = findViewById(R.id.buttonLED);
        buttonPUMP = findViewById(R.id.buttonPUMP);

        airHumidityGraph = (GraphView) findViewById(R.id.graph1);
        airHumidityGraph.getGridLabelRenderer().setHorizontalLabelsVisible(false);
        airHumidityGraph.getGridLabelRenderer().setGridColor(Color.WHITE);
        airHumidityGraph.getGridLabelRenderer().setVerticalLabelsColor(Color.WHITE);
        airHumidityGraph.getGridLabelRenderer().setHorizontalLabelsColor(Color.WHITE);
        airHumidityGraph.getGridLabelRenderer().setVerticalLabelsColor(Color.WHITE);
        airHumidityGraph.getGridLabelRenderer().setHorizontalLabelsColor(Color.WHITE);

        airTemperatureGraph = (GraphView) findViewById(R.id.graph2);
        airTemperatureGraph.getGridLabelRenderer().setHorizontalLabelsVisible(false);
        airTemperatureGraph.getGridLabelRenderer().setGridColor(Color.WHITE);
        airTemperatureGraph.getGridLabelRenderer().setVerticalLabelsColor(Color.WHITE);
        airTemperatureGraph.getGridLabelRenderer().setHorizontalLabelsColor(Color.WHITE);
        airTemperatureGraph.getGridLabelRenderer().setVerticalLabelsColor(Color.WHITE);
        airTemperatureGraph.getGridLabelRenderer().setHorizontalLabelsColor(Color.WHITE);

        soilTemperature = (GraphView) findViewById(R.id.graph3);
        soilTemperature.getGridLabelRenderer().setHorizontalLabelsVisible(false);
        soilTemperature.getGridLabelRenderer().setGridColor(Color.WHITE);
        soilTemperature.getGridLabelRenderer().setVerticalLabelsColor(Color.WHITE);
        soilTemperature.getGridLabelRenderer().setHorizontalLabelsColor(Color.WHITE);
        soilTemperature.getGridLabelRenderer().setVerticalLabelsColor(Color.WHITE);
        soilTemperature.getGridLabelRenderer().setHorizontalLabelsColor(Color.WHITE);

        soilHumidity = (GraphView) findViewById(R.id.graph4);
        soilHumidity.getGridLabelRenderer().setHorizontalLabelsVisible(false);
        soilHumidity.getGridLabelRenderer().setGridColor(Color.WHITE);
        soilHumidity.getGridLabelRenderer().setVerticalLabelsColor(Color.WHITE);
        soilHumidity.getGridLabelRenderer().setHorizontalLabelsColor(Color.WHITE);
        soilHumidity.getGridLabelRenderer().setVerticalLabelsColor(Color.WHITE);
        soilHumidity.getGridLabelRenderer().setHorizontalLabelsColor(Color.WHITE);





        buttonLED.setOnCheckedChangeListener(
                new CompoundButton.OnCheckedChangeListener() {
                    @Override
                    public void onCheckedChanged(CompoundButton compoundButton,
                                                 boolean b) {
                        if (b == true) {
                            sendDataMQTT("Fusioz/feeds/relay1", "ON");
                        } else {
                            sendDataMQTT("Fusioz/feeds/relay1", "OFF");
                        }
                    }
                });

        buttonPUMP.setOnCheckedChangeListener(
                new CompoundButton.OnCheckedChangeListener() {
                    @Override
                    public void onCheckedChanged(CompoundButton compoundButton,
                                                 boolean b) {
                        if (b == true) {
                            sendDataMQTT("Fusioz/feeds/relay2", "ON");
                        } else {
                            sendDataMQTT("Fusioz/feeds/relay2", "OFF");
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
                if (topic.contains("sensor1")){
                    double x = Double.parseDouble(message.toString());
                    LocalDateTime time = LocalDateTime.now();
                    Date y = convertLocalDateTime(time);
                    seriesAirHumidity.appendData(new DataPoint(y,x), true, 3, true);
                    airHumidityGraph.addSeries(seriesAirHumidity);
                    airHumidityGraph.onDataChanged(true, true);
                    txtAirHumidity.setText("Air Humidity: "  + message.toString() + "°C");
                }


                else if(topic.contains("sensor2")){

                    double x = Double.parseDouble(message.toString());
                    LocalDateTime time = LocalDateTime.now();
                    Date y = convertLocalDateTime(time);
                    seriesAirTemperature.appendData(new DataPoint(y,x), true, 3, true);
                    airTemperatureGraph.addSeries(seriesAirTemperature);
                    airTemperatureGraph.onDataChanged(true, true);
                    txtAirTemp.setText("Air Temperature: " + message.toString() + "%" );
                }

                else if(topic.contains("sensor3")){

                    double x = Double.parseDouble(message.toString());
                    LocalDateTime time = LocalDateTime.now();
                    Date y = convertLocalDateTime(time);
                    seriesSoilTemperature.appendData(new DataPoint(y,x), true, 3, true);
                    soilTemperature.addSeries(seriesSoilTemperature);
                    soilTemperature.onDataChanged(true, true);
                    txtSoilTemperature.setText("Soil Temperature: " + message.toString() + "%" );
                }
                else if(topic.contains("sensor4")){

                    double x = Double.parseDouble(message.toString());
                    LocalDateTime time = LocalDateTime.now();
                    Date y = convertLocalDateTime(time);
                    seriesSoilHumidity.appendData(new DataPoint(y,x), true, 3, true);
                    soilHumidity.addSeries(seriesSoilHumidity);
                    soilHumidity.onDataChanged(true, true);
                    txtSoilHumidity.setText("Soil Humidity: " + message.toString() + "%" );
                }

                else if(topic.contains("AI")){
                    txtAI.setText(message.toString());
                }

                else if(topic.contains("relay1")){
                    if (message.toString().equals("ON")){
                        buttonLED.setChecked(true);
                    }else{
                        buttonLED.setChecked(false);
                    }
                }

                else if(topic.contains("relay2")){
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