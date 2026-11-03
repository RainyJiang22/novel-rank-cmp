package com.novelrank.app.data

import android.content.Context

class AndroidSettingsStore(context: Context) : SettingsStore {
    private val preferences = context.applicationContext.getSharedPreferences("novelrank", Context.MODE_PRIVATE)
    override fun loadAddress(): String? = preferences.getString("service_address", null)
    override fun saveAddress(address: String) {
        check(preferences.edit().putString("service_address", address).commit()) { "Could not save preferences" }
    }
}
