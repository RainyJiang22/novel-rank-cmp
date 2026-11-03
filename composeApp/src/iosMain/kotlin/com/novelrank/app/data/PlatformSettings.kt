package com.novelrank.app.data

import platform.Foundation.NSUserDefaults

class IosSettingsStore : SettingsStore {
    private val defaults = NSUserDefaults.standardUserDefaults
    override fun loadAddress(): String? = defaults.stringForKey("novelrank.service_address")
    override fun saveAddress(address: String) {
        defaults.setObject(address, forKey = "novelrank.service_address")
    }
}
