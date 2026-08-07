/**
 * BLE «Красная кнопка» — имитация интеграции
 * Mobile: react-native-ble-manager
 * Web: Web Bluetooth API (если поддерживается)
 */

import { Platform } from 'react-native';

const BLE_SERVICE_UUID = '0000ffe0-0000-1000-8000-00805f9b34fb';
const BLE_CHAR_UUID = '0000ffe1-0000-1000-8000-00805f9b34fb';
const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://127.0.0.1:8001';

export interface BleDevice {
  mac: string;
  name: string;
  rssi?: number;
}

/** Сканирование — на web возвращает mock, на mobile — заглушка */
export async function scanBleDevices(): Promise<BleDevice[]> {
  if (Platform.OS === 'web') {
    if (typeof navigator !== 'undefined' && 'bluetooth' in navigator) {
      try {
        // Web Bluetooth — запрос устройства (требует user gesture)
        // const device = await (navigator as Navigator & { bluetooth: Bluetooth }).bluetooth.requestDevice({
        //   filters: [{ services: [BLE_SERVICE_UUID] }],
        // });
        // return [{ mac: device.id, name: device.name || 'Red Button' }];
      } catch {
        /* fallback mock */
      }
    }
    const resp = await fetch('http://localhost:8100/scan');
    if (resp.ok) {
      const data = await resp.json();
      return data.devices;
    }
  }
  // react-native-ble-manager: BleManager.scan([], 5, true)
  return [{ mac: 'AA:BB:CC:DD:EE:FF', name: 'HomeEase Red Button', rssi: -48 }];
}

export async function registerBleDevice(mac: string, token: string): Promise<void> {
  await fetch(`${API_URL}/api/v1/ble/register`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ device_mac: mac }),
  });
}

export async function simulateRedButtonPress(mac: string): Promise<Record<string, unknown>> {
  const url =
    Platform.OS === 'web'
      ? 'http://localhost:8100/simulate-press'
      : `${API_URL}/api/v1/ble/event`;
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ device_mac: mac, action: 'quiet_hour' }),
  });
  return resp.json();
}

export { BLE_SERVICE_UUID, BLE_CHAR_UUID };
