import { Linking, Platform, Pressable, StyleSheet, Text, View } from 'react-native';

type Props = {
  latitude: number;
  longitude: number;
  label?: string;
};

/** Открыть точку на OpenStreetMap (бесплатно, без API-ключа). */
export function OsmMapLink({ latitude, longitude, label }: Props) {
  const url = `https://www.openstreetmap.org/?mlat=${latitude}&mlon=${longitude}#map=15/${latitude}/${longitude}`;

  return (
    <View style={styles.box}>
      <Text style={styles.coords}>
        {label ? `${label}: ` : ''}
        {latitude.toFixed(4)}, {longitude.toFixed(4)}
      </Text>
      <Pressable style={styles.btn} onPress={() => Linking.openURL(url)}>
        <Text style={styles.btnText}>🗺 OpenStreetMap</Text>
      </Pressable>
      {Platform.OS === 'web' && (
        <iframe
          title="osm"
          width="100%"
          height="200"
          style={{ border: 0, borderRadius: 8, marginTop: 8 }}
          src={`https://www.openstreetmap.org/export/embed.html?bbox=${longitude - 0.01}%2C${latitude - 0.01}%2C${longitude + 0.01}%2C${latitude + 0.01}&layer=mapnik&marker=${latitude}%2C${longitude}`}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  box: { marginVertical: 8 },
  coords: { fontSize: 13, color: '#7A6568', marginBottom: 6 },
  btn: {
    backgroundColor: '#E8F4FA',
    padding: 10,
    borderRadius: 8,
    alignSelf: 'flex-start',
  },
  btnText: { color: '#3D6B8E', fontWeight: '600' },
});
