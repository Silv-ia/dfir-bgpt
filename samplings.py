# /content/dfir-bgpt/samplings.py
# GPT generated as substitute... 
# samplings.py

import torch
import numpy as np

def top_k_sampling(probs: np.ndarray, top_k: int = 0, return_probs: bool = False):
    if top_k > 0:
        indices = np.argpartition(probs, -top_k)[-top_k:]
        new_probs = np.zeros_like(probs)
        new_probs[indices] = probs[indices]
        new_probs = new_probs / new_probs.sum()
    else:
        new_probs = probs
    if return_probs:
        return new_probs
    return np.random.choice(len(new_probs), p=new_probs)

def top_p_sampling(probs: np.ndarray, top_p: float = 1.0, return_probs: bool = False):
    sorted_idx = np.argsort(probs)[::-1]
    sorted_probs = probs[sorted_idx]
    cum_probs = np.cumsum(sorted_probs)
    cutoff = (cum_probs > top_p).argmax() + 1
    keep_idx = sorted_idx[:cutoff]
    new_probs = np.zeros_like(probs)
    new_probs[keep_idx] = probs[keep_idx]
    new_probs = new_probs / new_probs.sum()
    if return_probs:
        return new_probs
    return np.random.choice(len(new_probs), p=new_probs)

def temperature_sampling(probs: np.ndarray, temperature: float = 1.0):
    if temperature <= 0:
        return probs.argmax()
    logits = np.log(probs + 1e-9) / temperature
    exp_logits = np.exp(logits)
    new_probs = exp_logits / exp_logits.sum()
    return np.random.choice(len(new_probs), p=new_probs)
