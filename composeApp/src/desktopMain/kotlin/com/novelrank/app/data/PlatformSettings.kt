package com.novelrank.app.data

import java.util.prefs.Preferences

class DesktopSettingsStore : SettingsStore {
    private val preferences = Preferences.userRoot().node("com/novelrank/app")
    override fun loadAddress(): String? = preferences.get("service_address", null)
    override fun saveAddress(address: String) {
        preferences.put("service_address", address)
        preferences.flush()
    }
}
