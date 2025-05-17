package com.example.marcus;

import android.telecom.Call;
import android.telecom.InCallService;
import android.util.Log;

import java.util.ArrayList;
import java.util.List;

public class MyInCallService extends InCallService {
    private static MyInCallService instance;
    private List<Call> callList = new ArrayList<>();

    @Override
    public void onCreate() {
        super.onCreate();
        instance = this;
    }

    @Override
    public void onCallAdded(Call call) {
        super.onCallAdded(call);
        callList.add(call);
        Log.d("MyInCallService", "Call added: " + call.toString());
        call.registerCallback(new Call.Callback() {
            @Override
            public void onStateChanged(Call call, int state) {
                super.onStateChanged(call, state);
                if (state == Call.STATE_DISCONNECTED) {
                    callList.remove(call);
                    Log.d("MyInCallService", "Call removed: " + call.toString());
                }
            }
        });
    }

    @Override
    public void onCallRemoved(Call call) {
        super.onCallRemoved(call);
        callList.remove(call);
        Log.d("MyInCallService", "Call removed: " + call.toString());
    }

    public static MyInCallService getInstance() {
        return instance;
    }

    public List<Call> getCallList() {
        return callList;
    }
}