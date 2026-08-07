export type PaymentProviderId = 'yookassa' | 'rustore' | 'tbank';

export type PaymentProviderInfo = {
  id: PaymentProviderId;
  name: string;
  supports_cancel: boolean;
  platforms: string[];
};

export type SubscriptionPlan = 'monthly' | 'yearly';

export type CountryPricingEntry = {
  currency: string;
  monthly: number;
  yearly: number;
  monthly_display: string;
  yearly_display: string;
};

export type SubscriptionPrices = {
  country_code: string;
  currency: string;
  monthly: string;
  yearly: string;
  monthly_amount: number;
  yearly_amount: number;
  vat_included: boolean;
  country_pricing: Record<string, CountryPricingEntry>;
  available_providers: PaymentProviderInfo[];
};

export type SubscriptionStatus = {
  status: string;
  plan: string | null;
  has_access: boolean;
  days_remaining: number;
  trial_end: string | null;
  end_date: string | null;
  country_code: string;
  trial_used: boolean;
  trial_days: number;
  pricing: { monthly: string; yearly: string; currency: string };
  available_providers: PaymentProviderInfo[];
  can_cancel: boolean;
  current_provider: string | null;
  vat_included: boolean;
};

export type CheckoutResult = {
  checkout_url: string;
  provider: string;
};
