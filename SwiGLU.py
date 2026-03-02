class SwiGLU(nn.Module):
    """
    SwiGLU Feed-Forward Network.

    Two paths:
      gate: SiLU(x @ W_gate) - controls flow
      up:   x @ W_up         - carries information

    Combined: gate * up -> W_down

    SiLU(x) = x * sigmoid(x), a smooth version of ReLU.
    """
    def __init__(self, d_model, hidden_dim):
        super().__init__()
        self.w_gate = nn.Linear(d_model, hidden_dim, bias=False)
        self.w_up   = nn.Linear(d_model, hidden_dim, bias=False)
        self.w_down = nn.Linear(hidden_dim, d_model, bias=False)

    def forward(self, x):
        gate = F.silu(self.w_gate(x))
        up   = self.w_up(x)
        return F.dropout(self.w_down(gate * up), p=DROPOUT, training=self.training)