// Release settings required by suite/SCENARIOS.md: R8 on, trust the loopback test CA,
// <profileable android:shell="true"/>, non-debuggable (release default).
const fs = require('fs');
const path = require('path');
const { withAndroidManifest, withGradleProperties, withDangerousMod } = require('expo/config-plugins');

const NSC = `<?xml version="1.0" encoding="utf-8"?>
<!-- Benchmark-only: trust the loopback asset server test CA (suite/tls/bench-ca.pem). -->
<network-security-config>
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
            <certificates src="@raw/bench_ca" />
        </trust-anchors>
    </base-config>
</network-security-config>
`;

function setProp(props, key, value) {
  const existing = props.find((p) => p.type === 'property' && p.key === key);
  if (existing) existing.value = value;
  else props.push({ type: 'property', key, value });
}

module.exports = function withBenchRelease(config) {
  config = withAndroidManifest(config, (cfg) => {
    const app = cfg.modResults.manifest.application[0];
    delete app.$['android:usesCleartextTraffic'];
    app.$['android:networkSecurityConfig'] = '@xml/network_security_config';
    app.profileable = [{ $: { 'android:shell': 'true' } }];
    return cfg;
  });
  config = withDangerousMod(config, ['android', async (cfg) => {
    const res = path.join(cfg.modRequest.platformProjectRoot, 'app/src/main/res');
    fs.mkdirSync(path.join(res, 'xml'), { recursive: true });
    fs.mkdirSync(path.join(res, 'raw'), { recursive: true });
    fs.writeFileSync(path.join(res, 'xml/network_security_config.xml'), NSC);
    fs.copyFileSync(path.join(cfg.modRequest.projectRoot, '../../suite/tls/bench-ca.pem'), path.join(res, 'raw/bench_ca.pem'));
    return cfg;
  }]);
  config = withGradleProperties(config, (cfg) => {
    setProp(cfg.modResults, 'android.enableMinifyInReleaseBuilds', 'true');
    setProp(cfg.modResults, 'newArchEnabled', 'true');
    setProp(cfg.modResults, 'hermesEnabled', 'true');
    return cfg;
  });
  return config;
};
