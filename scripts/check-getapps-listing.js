const fs = require('fs');
const path = require('path');
const file = path.join(__dirname, '..', 'stores', 'getapps', 'listing.json');
const listing = JSON.parse(fs.readFileSync(file, 'utf8'));
const required = [
  'package_name',
  'app_name',
  'privacy_url',
  'brief',
  'description',
  'keywords',
  'build_profile',
  'build_type',
];
const missing = required.filter((key) => !listing[key] || String(listing[key]).trim() === '');
if (missing.length) {
  console.error('GetApps listing incomplete:', missing.join(', '));
  process.exit(1);
}
if (listing.publish !== false) {
  console.error('GetApps listing must keep publish=false until store upload is requested.');
  process.exit(1);
}
if (listing.package_name !== 'com.homeease.app') {
  console.error('GetApps package_name must match Android package com.homeease.app');
  process.exit(1);
}
if (!String(listing.privacy_url).startsWith('https://')) {
  console.error('GetApps privacy_url must start with https://');
  process.exit(1);
}
if (String(listing.brief).length > 34) {
  console.error('GetApps brief is longer than 34 characters');
  process.exit(1);
}
if (String(listing.description).length < 20 || String(listing.description).length > 4000) {
  console.error('GetApps description length is out of 20-4000');
  process.exit(1);
}
console.log('GETAPPS_LISTING_OK');
