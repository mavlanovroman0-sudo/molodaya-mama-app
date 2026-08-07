import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  FlatList,
  Pressable,
  StyleSheet,
  Switch,
  Text,
  View,
} from 'react-native';
import * as Location from 'expo-location';
import { useTranslation } from '../../hooks/useTranslation';
import { OsmMapLink } from '../../components/OsmMapLink';
import { ErrorState } from '../../components/ErrorState';
import { api } from '../../services/api';
import { useAppStore } from '../../store/appStore';

type Nanny = {
  id: string;
  display_name: string;
  distance_km: number;
  latitude: number;
  longitude: number;
};

export function NannyScreen() {
  const { t } = useTranslation();
  const token = useAppStore((s) => s.token);
  const [nannies, setNannies] = useState<Nanny[]>([]);
  const [isNanny, setIsNanny] = useState(false);
  const [coords, setCoords] = useState<{ lat: number; lon: number } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadNannies = useCallback(async () => {
    if (!token) return;
    setError(null);
    try {
      const data = await api.get<{ nannies: Nanny[] }>('/api/v1/nannies', { token });
      setNannies(data.nannies);
    } catch (e) {
      setError(e instanceof Error ? e.message : t('common.error_generic'));
    }
  }, [token, t]);

  const toggleNanny = async (value: boolean) => {
    setIsNanny(value);
    if (!token) return;
    await api.put('/api/v1/user/nanny', { is_nanny: value }, { token });
    await loadNannies();
  };

  useEffect(() => {
    (async () => {
      try {
        if (token) {
          const { status } = await Location.requestForegroundPermissionsAsync();
          if (status === 'granted') {
            const loc = await Location.getCurrentPositionAsync({});
            setCoords({ lat: loc.coords.latitude, lon: loc.coords.longitude });
            await api.put(
              '/api/v1/user/location',
              { latitude: loc.coords.latitude, longitude: loc.coords.longitude },
              { token }
            );
          }
          await loadNannies();
        }
      } finally {
        setLoading(false);
      }
    })();
  }, [loadNannies, token]);

  const requestNanny = async (nannyId: string) => {
    if (!token) return;
    await api.post(
      '/api/v1/nannies/request',
      { to_user_id: nannyId, message: t('screens.nanny_request_msg') },
      { token }
    );
    Alert.alert(t('screens.nanny_request_sent'));
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color="#7EB8DA" />
      </View>
    );
  }

  if (error && nannies.length === 0) {
    return <ErrorState message={error} onRetry={loadNannies} />;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t('tabs.nanny')}</Text>
      <View style={styles.nannyToggle}>
        <Text>{t('screens.i_am_nanny')}</Text>
        <Switch value={isNanny} onValueChange={toggleNanny} />
      </View>
      {coords && <OsmMapLink latitude={coords.lat} longitude={coords.lon} label={t('screens.your_location')} />}
      <FlatList
        data={nannies}
        keyExtractor={(n) => n.id}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>{item.display_name}</Text>
            <Text style={styles.cardMeta}>{item.distance_km} km</Text>
            <OsmMapLink latitude={item.latitude} longitude={item.longitude} />
            <Pressable style={styles.reqBtn} onPress={() => requestNanny(item.id)}>
              <Text style={styles.reqBtnText}>{t('screens.send_request')}</Text>
            </Pressable>
          </View>
        )}
        ListEmptyComponent={<Text style={styles.empty}>{t('screens.no_nannies')}</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8F4F0', padding: 16, paddingTop: 8 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  title: { fontSize: 24, fontWeight: '700', color: '#3D2C2E', marginBottom: 12 },
  nannyToggle: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#fff', padding: 14, borderRadius: 12, marginBottom: 12 },
  card: { backgroundColor: '#fff', borderRadius: 12, padding: 14, marginBottom: 10 },
  cardTitle: { fontSize: 16, fontWeight: '600' },
  cardMeta: { fontSize: 13, color: '#7A6568', marginTop: 4 },
  reqBtn: { marginTop: 8, backgroundColor: '#7EB8DA', padding: 10, borderRadius: 8, alignSelf: 'flex-start' },
  reqBtnText: { color: '#fff', fontWeight: '600' },
  empty: { textAlign: 'center', color: '#7A6568', marginTop: 30 },
});
