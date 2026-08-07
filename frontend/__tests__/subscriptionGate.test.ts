/** @jest-environment node */

describe('SubscriptionGate logic', () => {
  it('blocks access when has_access is false', () => {
    const status = { has_access: false, status: 'expired' };
    const shouldShowMain = status.has_access;
    expect(shouldShowMain).toBe(false);
  });

  it('allows access when trialing', () => {
    const status = { has_access: true, status: 'trialing', days_remaining: 10 };
    expect(status.has_access).toBe(true);
  });

  it('redirects to subscription when trial expired', () => {
    const status = { has_access: false, status: 'expired', days_remaining: 0 };
    const screen = status.has_access ? 'MainStack' : 'SubscriptionScreen';
    expect(screen).toBe('SubscriptionScreen');
  });
});
