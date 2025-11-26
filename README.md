# NGINX + 3 Apps + Fluent-Bit + Elasticsearch + Kibana

### Complete Multi-Container Logging & Application Stack

---

## 📌 **Overview**

This project contains:

1. **NGINX** – Reverse proxy that routes traffic to 3 different apps
2. **Three Applications**

   * **app1** → Blue page + some info
   * **app2** → Red page + some info
   * **app3** → Green page + some info
   * Each app includes a **button with 3:2:1 wait counter** before navigating to next app
3. **Fluent-Bit** (one per app) – Collects logs from each app
4. **Elasticsearch (ES)** – Stores logs
5. **Kibana** – View, search, and visualize logs
6. **Docker Compose** – Runs everything together

---

## 📂 **Project Structure**

```
project-root/
│
├── docker-compose.yml
│
├── app1/
│   ├── Dockerfile
│   └── src/
│       └── index.html
│
├── app2/
│   ├── Dockerfile
│   └── src/
│       └── index.html
│
├── app3/
│   ├── Dockerfile
│   └── src/
│       └── index.html
│
├── fluent-bit/
│   ├── app1.conf
│   ├── app2.conf
│   └── app3.conf
│
└── nginx/
    └── nginx.conf
```

---

# 🚀 SYSTEM FLOW

```
User → NGINX → app1 → app2 → app3
             ↓
          Log files
             ↓
        Fluent-Bit
             ↓
      Elasticsearch
             ↓
          Kibana
```

---

# 🧩 COMPONENT DETAILS

---

## 1️⃣ **NGINX Reverse Proxy**

* Receives all incoming traffic on **port 80**
* Routes:

  * `/app1` → app1
  * `/app2` → app2
  * `/app3` → app3

### Main Job

✔ Acts as a **gateway** to all apps
✔ Controls navigation
✔ Easy to test all 3 apps using one entry point

---

## 2️⃣ **Application Containers (app1, app2, app3)**

Each app:

* Runs a small web server
* Shows:

  * Background color (blue, red, green)
  * Some informational text
* Contains a **button**

  * When clicked → starts **3 → 2 → 1** countdown
  * After countdown → navigates to next app

### Example Flow

* User visits **/app1**
* Clicks button → waits 3 seconds → moves to **/app2**
* From app2 → button → 3 seconds → moves to **/app3**
* From app3 → can loop back to app1

### Logging

Each app writes a log file:

```
/var/log/appX/appX.log
```

---

## 3️⃣ **Fluent-Bit (One Container Per App)**

### Why ONE Fluent-Bit per app?

✔ Isolates logs
✔ Avoids permission conflicts
✔ Clear separation

### What Fluent-Bit does:

* Watches log files:

  ```
  /var/log/app1/app1.log
  ```
* Sends logs to:
  ✔ Elasticsearch

### About the image

Fluent-Bit uses a **distroless image**.
This means:

❌ No `bash`
❌ No `sh`
❌ No `ls`
❌ No shell at all

It ONLY runs its internal Fluent-Bit engine.

**That’s why `docker exec -it fluentbit /bin/sh` fails — not your mistake.**

---

## 4️⃣ **Elasticsearch (ES)**

* Stores logs from all apps
* Each app gets its own index:

  ```
  app1-logs
  app2-logs
  app3-logs
  ```

---

## 5️⃣ **Kibana**

* Connects to Elasticsearch
* Lets you:
  ✔ Search logs
  ✔ Filter logs
  ✔ Create dashboards
  ✔ Monitor errors

---

# ⚙ **Configuration Explanation**

### ✔ Docker Compose

* Starts:

  * 3 app containers
  * 3 Fluent-Bit containers
  * 1 NGINX
  * 1 Elasticsearch
  * 1 Kibana

* Creates log volumes:

  ```
  app1_logs
  app2_logs
  app3_logs
  ```

These log volumes are **shared between app and fluent-bit**, example:

```
app1 container writes → app1_logs volume → fluentbit1 reads → sends to ES
```

---

### ✔ Fluent-Bit Config Example

```
[INPUT]
    Name tail
    Path /var/log/app1/app1.log
    Tag app1

[OUTPUT]
    Name es
    Match app1
    Host elasticsearch
    Port 9200
    Index app1-logs
```

Meaning:

* Watch the file
* Whenever new logs appear → send to Elasticsearch index `app1-logs`

---

### ✔ App Button Code (Simplified)

JavaScript:

```
let countdown = 3;

function startCountdown() {
    let interval = setInterval(() => {
        button.innerText = countdown;
        countdown--;

        if (countdown === 0) {
            clearInterval(interval);
            window.location.href = "/app2";
        }
    }, 1000);
}
```

This:

✔ Shows 3 → 2 → 1
✔ Redirects to next page

---

# 🧪 **Testing the System**

## 1. Test apps

Open:

```
http://localhost/app1
http://localhost/app2
http://localhost/app3
```

Click button → check countdown → next page loads.

---

## 2. Test logs

Run:

```
docker compose exec app1 tail -n 20 /var/log/app1/app1.log
```

You should see:

```
[INFO] app1 loaded
[INFO] button clicked
```

If logs exist → Fluent-Bit will catch them.

---

## 3. Test Fluent-Bit → Elasticsearch

Go to Kibana:

```
http://localhost:5601
```

Create index pattern:

```
app1-logs*
```

Check logs.

---

# ✔ FINAL RESULT

You now have:

* A 3-app system
* Navigating through NGINX
* With colors and 3-2-1 button
* Logs stored persistently
* Fluent-Bit shipping logs
* Elasticsearch storing logs
* Kibana visualizing logs

---

# SIMPLE EXPLANATION (VERY EASY WORDS)

Here is everything explained as if you are **completely new to DevOps**:

---

## 🧠 **Whole Project in Simple Words**

### 👉 You have 3 small websites

* app1 (blue)
* app2 (red)
* app3 (green)

Each one shows information and a button.

When the button is clicked:

➡ it waits 3 seconds
➡ goes to the next site automatically

---

## 👉 NGINX is the Gatekeeper

Instead of running 3 different servers,
NGINX gives you one entry point:

```
/app1
/app2
/app3
```

It forwards the user to the correct app.

---

## 👉 Each App Creates Logs

Whenever someone visits or clicks a button, the app writes:

```
app1.log
app2.log
app3.log
```

These are stored in shared volumes.

---

## 👉 Fluent-Bit picks logs and sends to Elasticsearch

Think of Fluent-Bit as a **log delivery guy**:

* Watches log files
* Sends them to Elasticsearch

There is **one Fluent-Bit per app** → clean separation.

---

## 👉 Elasticsearch stores everything permanently

All logs go into databases:

```
app1-logs
app2-logs
app3-logs
```

---

## 👉 Kibana shows the logs

You can search:

* How many clicks?
* Who visited which app?
* Errors?
* Activity dashboard?

---

## 👉 Docker Compose runs everything automatically

One command starts the entire system:

```
docker compose up -d
```

---

