/* Legal Timekeeper: deployment settings.
   CLIENT_ID comes from the Microsoft Entra app registration (see TIMEKEEPER.md at the repository root).
   Leave it blank and the app runs in on-device mode with sign-in hidden. */
export const CONFIG = {
  CLIENT_ID: 'cfc6cf5e-cfbf-45a4-969c-14481512cb69', // Entra app "MyLegalTimekeeper"
  // "common" lets any Microsoft account sign in: personal (Outlook.com) and work or school.
  AUTHORITY: 'https://login.microsoftonline.com/common',
  SCOPES: ['openid', 'profile', 'offline_access', 'Files.ReadWrite.AppFolder'],
  // Must match the redirect URI registered as a "Single-page application" in Entra.
  REDIRECT_URI: new URL('./', location.href).href.split('?')[0].split('#')[0],
  GRAPH: 'https://graph.microsoft.com/v1.0',
  SYNC_FILE: 'timekeeper-data.json',
  // Origins allowed to hand over entries from the old app (see the forwarding page).
  LEGACY_ORIGINS: ['https://jasontbarnes.com', 'https://www.jasontbarnes.com', 'https://jasontbarnesesq.github.io'],
  VERSION: '2.1.0',
};
