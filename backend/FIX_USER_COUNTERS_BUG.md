# Fix: User Counters Only Returning One User

## Problem
The endpoint `/api/counters/users/{printer_id}` was only returning 1 user instead of all users from the latest reading session.

## Root Cause
The function `get_user_counters_latest()` in `backend/services/counter_service.py` was using `fecha_lectura` to find all users from the same reading session. However, `fecha_lectura` has microsecond precision, and each user record gets a slightly different timestamp during insertion:

```
User 1: 2026-03-02T20:58:57.988777Z
User 2: 2026-03-02T20:58:57.988730Z
User 3: 2026-03-02T20:58:57.988681Z
```

The query `fecha_lectura == latest[0]` only matched the exact timestamp, returning only 1 user.

## Solution
Changed the query to use `created_at` instead of `fecha_lectura`. All records from the same reading session have the exact same `created_at` timestamp.

## File Changed
`backend/services/counter_service.py` - Line ~497

### Before:
```python
@staticmethod
def get_user_counters_latest(db: Session, printer_id: int) -> List[ContadorUsuario]:
    # Obtener la fecha de la última lectura
    latest = db.query(ContadorUsuario.fecha_lectura).filter(
        ContadorUsuario.printer_id == printer_id
    ).order_by(ContadorUsuario.fecha_lectura.desc()).first()
    
    if not latest:
        return []
    
    # Obtener todos los contadores de esa fecha
    return db.query(ContadorUsuario).filter(
        ContadorUsuario.printer_id == printer_id,
        ContadorUsuario.fecha_lectura == latest[0]
    ).all()
```

### After:
```python
@staticmethod
def get_user_counters_latest(db: Session, printer_id: int) -> List[ContadorUsuario]:
    # Obtener el created_at de la última lectura
    # Usamos created_at en lugar de fecha_lectura porque todos los registros
    # de una misma sesión de lectura tienen el mismo created_at
    latest = db.query(ContadorUsuario.created_at).filter(
        ContadorUsuario.printer_id == printer_id
    ).order_by(ContadorUsuario.created_at.desc()).first()
    
    if not latest:
        return []
    
    # Obtener todos los contadores de esa sesión de lectura
    return db.query(ContadorUsuario).filter(
        ContadorUsuario.printer_id == printer_id,
        ContadorUsuario.created_at == latest[0]
    ).all()
```

## How to Apply

### If running backend locally:
The change is already in the file. Just restart the backend:
1. Stop the backend (Ctrl+C)
2. Run `backend/start-backend.bat`

### If running backend in Docker:
The change is already in the file (mounted volume). Restart the container:
```bash
docker restart ricoh-backend
```

Wait 10 seconds for the container to fully restart, then test:
```bash
curl http://localhost:8000/api/counters/users/4 | ConvertFrom-Json | Measure-Object
```

Should return Count > 1 (around 265 users for printer 4).

## Verification
After applying the fix:
1. Open the frontend: http://localhost:5174
2. Navigate to "Contadores" menu
3. Click on any printer card
4. Scroll down to "Contadores por Usuario" table
5. Should see multiple users with their page counts

## Status
- [x] Code change made
- [x] Backend restarted successfully  
- [x] Fix verified: API returns 265 users for printer 4
- [ ] Frontend showing user counters (needs verification)
