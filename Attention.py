def scaled_dot_prod_attention(q, k ,v , mask = None):
    """Implement Scaled Dot Product Attention"""
    d_k = query.size(-1)
    scores = torch.matmul(q,k.transpose(-2 , -1))/d_k ** 0.5
    if mask is not None:
        scores = scores.masked_fill(mask == 0 , float('-inf'))

    attention_weights = F.softmax(scores , dim = 1)
    attention_weights = attention_weights.dropout(0.1)
    output = torch.matmul(attention_weights , v)
    return output , attention_weights
