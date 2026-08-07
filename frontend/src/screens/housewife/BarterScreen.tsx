import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  FlatList,
  Pressable,
  RefreshControl,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import * as Location from 'expo-location';
import { useTranslation } from '../../hooks/useTranslation';
import { OsmMapLink } from '../../components/OsmMapLink';
import { ErrorState } from '../../components/ErrorState';
import { useApiList } from '../../hooks/useApiList';
import { api } from '../../services/api';
import { useAppStore } from '../../store/appStore';

type Ad = {
  id: string;
  title: string;
  description: string | null;
  ad_type: string;
  category: string | null;
  location_lat: number | null;
  location_lon: number | null;
};

export function BarterScreen() {
  const { t } = useTranslation();
  const token = useAppStore((s) => s.token);
  const [ads, setAds] = useState<Ad[]>([]);
  const [filter, setFilter] = useState<'all' | 'offer' | 'request'>('all');
  const [title, setTitle] = useState('');
  const [geoLoading, setGeoLoading] = useState(true);
  const [coords, setCoords] = useState<{ lat: number; lon: number } | null>(null);

  const loadAds = useCallback(async () => {
    const path =
      filter === 'all' ? '/api/v1/barter/ads' : `/api/v1/barter/ads?ad_type=${filter}`;
    return api.get<Ad[]>(path, token ? { token } : undefined);
  }, [filter, token]);

  const { data, loading, refreshing, error, reload, refresh } = useApiList(loadAds, !!token);
  useEffect(() => {
    setAds(data);
  }, [data]);

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
        }
      } finally {
        setGeoLoading(false);
      }
    })();
  }, [token]);

  const createAd = async () => {
    if (!token || !title.trim()) return;
    await api.post(
      '/api/v1/barter/ads',
      {
        title: title.trim(),
        ad_type: 'offer',
        location_lat: coords?.lat,
        location_lon: coords?.lon,
      },
      { token }
    );
    setTitle('');
    await reload();
    Alert.alert(t('screens.saved'));
  };

  const requestExchange = async (adId: string) => {
    if (!token) return;
    await api.post(`/api/v1/barter/ads/${adId}/request?jetons_amount=0`, undefined, { token });
    Alert.alert(t('screens.barter_request_sent'));
  };

  if (loading || geoLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color="#D4919A" />
      </View>
    );
  }

  if (error && ads.length === 0) {
    return <ErrorState message={error} onRetry={reload} />;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{t('tabs.barter')}</Text>
      <View style={styles.filters}>
        {(['all', 'offer', 'request'] as const).map((f) => (
          <Pressable
            key={f}
            style={[styles.chip, filter === f && styles.chipActive]}
            onPress={() => setFilter(f)}
          >
            <Text style={[styles.chipText, filter === f && styles.chipTextActive]}>
              {t(`screens.barter_${f}`)}
            </Text>
          </Pressable>
        ))}
      </View>
      {token && (
        <View style={styles.row}>
          <TextInput style={styles.input} placeholder={t('screens.barter_title')} value={title} onChangeText={setTitle} />
          <Pressable style={styles.addBtn} onPress={createAd}>
            <Text style={styles.addBtnText}>+</Text>
          </Pressable>
        </View>
      )}
      {coords && <OsmMapLink latitude={coords.lat} longitude={coords.lon} label={t('screens.your_location')} />}
      <FlatList
        data={ads}
        keyExtractor={(a) => a.id}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={refresh} tintColor="#D4919A" />}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>{item.title}</Text>
            <Text style={styles.cardMeta}>{item.ad_type} · {item.category || '—'}</Text>
            {item.location_lat != null && item.location_lon != null && (
              <OsmMapLink latitude={item.location_lat} longitude={item.location_lon} />
            )}
            {token && (
              <Pressable style={styles.reqBtn} onPress={() => requestExchange(item.id)}>
                <Text style={styles.reqBtnText}>{t('screens.barter_request')}</Text>
              </Pressable>
            )}
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F8F4F0', padding: 16, paddingTop: 8 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  title: { fontSize: 24, fontWeight: '700', color: '#3D2C2E', marginBottom: 12 },
  filters: { flexDirection: 'row', marginBottom: 12, gap: 8 },
  chip: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 16, backgroundColor: '#fff' },
  chipActive: { backgroundColor: '#D4919A' },
  chipText: { color: '#7A6568', fontSize: 13 },
  chipTextActive: { color: '#fff' },
  row: { flexDirection: 'row', marginBottom: 12 },
  input: { flex: 1, backgroundColor: '#fff', borderRadius: 10, padding: 12, marginRight: 8 },
  addBtn: { backgroundColor: '#D4919A', borderRadius: 10, width: 44, justifyContent: 'center', alignItems: 'center' },
  addBtnText: { color: '#fff', fontSize: 22 },
  card: { backgroundColor: '#fff', borderRadius: 12, padding: 14, marginBottom: 10 },
  cardTitle: { fontSize: 16, fontWeight: '600' },
  cardMeta: { fontSize: 12, color: '#7A6568', marginTop: 4 },
  reqBtn: { marginTop: 8, alignSelf: 'flex-start', backgroundColor: '#E8F4FA', padding: 8, borderRadius: 8 },
  reqBtnText: { color: '#3D6B8E', fontWeight: '600' },
});
