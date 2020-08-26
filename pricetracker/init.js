/**
 * Initial script to hide automation (identity of webdriver)
 * References:
 * https://intoli.com/blog/not-possible-to-block-chrome-headless/
 * https://antoinevastel.com/bot%20detection/2018/01/17/detect-chrome-headless-v2.html
 * https://github.com/fingerprintjs/fingerprintjs2
 * https://github.com/mozilla/geckodriver/issues/1680
 * https://stackoverflow.com/questions/33225947/can-a-website-detect-when-you-are-using-selenium-with-chromedriver
 */

Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined,
});
Object.defineProperty(navigator, 'languages', {
    get: () => [navigator.language, 'en-US', 'en'],
});
Object.defineProperty(navigator, 'plugins', {
    get: () => ['1', '2'],
});
// window.navigator.chrome = {
//     runtime: {
//         PlatformOs: {
//             MAC: 'mac',
//             WIN: 'win',
//             ANDROID: 'android',
//             CROS: 'cros',
//             LINUX: 'linux',
//             OPENBSD: 'openbsd',
//         },
//         PlatformArch: {
//             ARM: 'arm',
//             X86_32: 'x86-32',
//             X86_64: 'x86-64',
//         },
//         PlatformNaclArch: {
//             ARM: 'arm',
//             X86_32: 'x86-32',
//             X86_64: 'x86-64',
//         },
//         RequestUpdateCheckStatus: {
//             THROTTLED: 'throttled',
//             NO_UPDATE: 'no_update',
//             UPDATE_AVAILABLE: 'update_available',
//         },
//         OnInstalledReason: {
//             INSTALL: 'install',
//             UPDATE: 'update',
//             CHROME_UPDATE: 'chrome_update',
//             SHARED_MODULE_UPDATE: 'shared_module_update',
//         },
//         OnRestartRequiredReason: {
//             APP_UPDATE: 'app_update',
//             OS_UPDATE: 'os_update',
//             PERIODIC: 'periodic',
//         },
//     }
// };
// const originalQuery = window.navigator.permissions.query;
// window.navigator.permissions.query = (parameters) => (
//     parameters.name === 'notifications' ?
//         Promise.resolve({ state: Notification.permission }) :
//         originalQuery(parameters)
// );