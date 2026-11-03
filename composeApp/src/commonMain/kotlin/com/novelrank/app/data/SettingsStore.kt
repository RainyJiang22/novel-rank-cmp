package com.novelrank.app.data

import io.ktor.client.HttpClient

const val CLOUD_SERVICE_ADDRESS = "https://47.251.189.239/novelrank"

interface SettingsStore {
    fun loadAddress(): String?
    fun saveAddress(address: String)
}

data class ClientEnvironment(
    val store: SettingsStore,
    val defaultAddress: String,
    val allowHttp: Boolean,
)

expect fun createPlatformHttpClient(): HttpClient
