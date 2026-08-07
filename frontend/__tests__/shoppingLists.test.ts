/** @jest-environment node */
import { api } from '../src/services/api';

jest.mock('../src/services/api', () => ({
  api: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));

type ListRow = { id: string; name: string; items_count: number };

describe('ShoppingLists API', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('loads shopping lists with token', async () => {
    const mockLists: ListRow[] = [{ id: '1', name: 'Продукты', items_count: 3 }];
    (api.get as jest.Mock).mockResolvedValue(mockLists);

    const data = await api.get<ListRow[]>('/api/v1/shopping/lists', { token: 'tok' });

    expect(data).toHaveLength(1);
    expect(data[0].name).toBe('Продукты');
    expect(api.get).toHaveBeenCalledWith('/api/v1/shopping/lists', { token: 'tok' });
  });

  it('handles API error', async () => {
    (api.get as jest.Mock).mockRejectedValue(new Error('Network error'));
    await expect(api.get('/api/v1/shopping/lists', { token: 'x' })).rejects.toThrow('Network error');
  });
});
