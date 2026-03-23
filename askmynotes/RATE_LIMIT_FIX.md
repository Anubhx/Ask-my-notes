# 🚨 Fix: Gemini API Rate Limit (429 Error)

## ❌ The Problem

You're getting a **429 Rate Limit Error**:
```
Quota exceeded for quota metric 'Generate Content API requests per minute'
limit: 'GenerateContent request limit per minute' = 0
```

This means the **free tier Gemini API has hit its limit** (sometimes 0 requests per minute).

---

## ✅ Solutions (in order of ease)

### Solution 1: Wait & Retry (Simplest)
The app now has **automatic retry logic with exponential backoff**.

**What happens:**
- On rate limit error, app waits 2 seconds
- Tries again (up to 3 attempts)
- Shows you a message: "⏳ API rate limit hit. Waiting 2s before retry..."

**Try these:**
1. Wait 5-10 minutes
2. Refresh the browser
3. Ask your question again

---

### Solution 2: Use a Fresh API Key from Different Google Account
Each Google account gets its **own quota** (usually higher on first use).

**Steps:**
1. Go to https://ai.google.dev
2. **Sign in with a DIFFERENT Google account** (you have 2 accounts, use the other one)
3. Click "Get API Key"
4. Copy the new key
5. Update `.env` in your project:
   ```
   GOOGLE_API_KEY=your_new_key_here
   ```
6. Refresh the Streamlit app (browser)
7. Try your query again

---

### Solution 3: Request Quota Increase
For paid customers only (takes 5-10 minutes to process):

1. Go to: https://cloud.google.com/docs/quotas/help/request_increase
2. Select your Google Cloud project
3. Request increase for "Generate Content API requests per minute"
4. Wait for approval

---

### Solution 4: Upgrade to Paid Tier
If you plan to use this frequently:

1. Visit https://ai.google.dev/pricing
2. Set up a paid API key with billing
3. Provides much higher limits (thousands of requests/minute)

---

## 📊 Free Tier Limits

| Metric | Free Tier | Paid Tier |
|--------|-----------|-----------|
| Requests/min | 60 | 1,000+ |
| Requests/day | Unlimited | Unlimited (if quota allows) |
| Cost | Free | Pay per request |
| Regional limits | Yes (sometimes 0) | No |

**Note:** Free tier limits vary by region. Your region (asia-southeast1) shows limit of 0 requests/min, but it should increase over time.

---

## 🔧 What Was Fixed in the Code

I added **smart retry logic** to `app.py`:

```python
def call_gemini_with_retry(prompt, max_retries=3, initial_wait=2):
    """Call Gemini with exponential backoff on rate limit."""
    for attempt in range(max_retries):
        try:
            # Try to call Gemini
            response = model.generate_content(prompt)
            return response.text
        
        except RateLimitError:
            # If rate limit, wait longer and retry
            wait_time = 2 ** attempt  # 2s, 4s, 8s...
            st.warning(f"Rate limit. Waiting {wait_time}s...")
            time.sleep(wait_time)
```

**Benefits:**
- ✅ Automatically retries 3 times
- ✅ Waits longer between retries (exponential backoff)
- ✅ Shows user a message while waiting
- ✅ Better error messages explaining the issue

---

## 🎯 Quick Steps to Get Working

### Fastest Solution (Use Different Account)
```
1. You have 2 Google IDs, right?
2. Go to https://ai.google.dev
3. Log in with your OTHER Google account
4. Get a new API key
5. Update .env:
   echo "GOOGLE_API_KEY=new_key_here" > .env
6. Refresh browser
7. Try your question again
```

Expected to work since new account = fresh quota.

---

## 📝 Current App Behavior

The app now:
1. Tries to call Gemini
2. **If 429 rate limit error:**
   - Waits 2 seconds
   - Tries again
   - Shows message: "⏳ API rate limit hit. Waiting 2s before retry 1/3..."
   - If fails again: waits 4 seconds, tries again
   - If fails again: waits 8 seconds, tries last time
3. **If successful:** Shows answer
4. **If all retries fail:** Shows helpful message with solutions

---

## ✨ Error Message You'll Now See

Instead of just "Error calling Gemini API", you'll see:

**If Rate Limited:**
```
❌ API Rate Limit Exceeded

Reason: Free tier Gemini API has strict limits 
(sometimes 0 requests/minute).

Solutions:
1. Wait a few minutes and try again
2. Use a different Google account with fresh API key
3. Request quota increase (see link)
4. Use paid API key
```

**If Other Error:**
```
Error calling Gemini API: [specific error]
Make sure your API key is valid and try again 
in a few moments.
```

---

## 🔍 Test It Out

After updating your `.env` with new API key:

1. Run Streamlit:
   ```bash
   streamlit run app.py
   ```

2. Upload a PDF

3. Ask a simple question like: "What is this document about?"

4. This time it should work! ✅

---

## 📞 If It Still Doesn't Work

**Still getting 429 error after waiting/retrying?**

1. **Confirm your API key is from a different Google account**
   - The free tier identifies you by account, not key
   - Using same account = same quota limits

2. **Check the free tier is actually enabled**
   - Go to https://ai.google.dev
   - Click "Get API Key"
   - Should show "Your API key is ready to use"

3. **Try a completely fresh Google account**
   - Create new Gmail account
   - Go to ai.google.dev
   - Get fresh API key
   - Use that key

---

## ✅ Summary

Your app now has:
- ✅ Automatic retry logic (3 attempts with 2s, 4s, 8s waits)
- ✅ Better error messages (specifically for rate limits)
- ✅ Clear next steps if rate limited

**Recommended next step:** Use a fresh API key from your second Google account.

Run the app and try again! 🚀
