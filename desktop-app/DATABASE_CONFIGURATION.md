# 🗄️ Database Configuration: PostgreSQL (Railway) + ChromaDB

## 🎯 Current Database Architecture

Our **Sentient Supercharged Phoenix System** uses a **dual-database architecture** for optimal performance and functionality:

### Primary Database: PostgreSQL (Railway)
- **Provider**: Railway.app
- **Type**: PostgreSQL
- **Purpose**: Mission persistence, tracking, and system logging
- **Connection**: `postgresql://postgres:LSvFcJSLjYBxsWrcTtgBUgLlLYBdPqiS@trolley.proxy.rlwy.net:44667/railway`

### Vector Database: ChromaDB
- **Type**: Local ChromaDB instance
- **Purpose**: Vector memory for learning and context retrieval
- **Location**: `db/chroma_memory/`
- **Connection**: `http://localhost:8000`

## 🏗️ Database Integration

### Configuration Files
- **`.env`**: Contains `DATABASE_URL` for PostgreSQL connection
- **`src/models/advanced_database.py`**: Main database management class
- **`config/settings.py`**: Database configuration settings

### Key Features
- **Automatic Detection**: System detects PostgreSQL vs SQLite based on URL
- **Dual Storage**: Missions in PostgreSQL, vector memory in ChromaDB
- **Real-time Updates**: Live mission status tracking
- **Error Recovery**: Robust error handling and connection management

## 📊 Database Schema

### PostgreSQL Tables

#### `missions`
- `id` (Primary Key)
- `mission_id_str` (Unique identifier)
- `title` (Mission title)
- `description` (Mission description)
- `prompt` (User prompt)
- `agent_type` (Agent type used)
- `status` (pending, planning, executing, completed, failed)
- `result` (Mission result)
- `plan` (Execution plan JSON)
- `execution_time` (Seconds)
- `tokens_used` (Token count)
- `error_message` (Error details)
- `created_at` (Creation timestamp)
- `updated_at` (Last update)
- `completed_at` (Completion timestamp)
- `is_archived` (Archive flag)

#### `mission_updates`
- `id` (Primary Key)
- `mission_id_str` (Mission reference)
- `update_message` (Update text)
- `update_type` (info, warning, error, success)
- `timestamp` (Update timestamp)
- `agent_role` (Agent role)
- `step_number` (Execution step)

#### `system_logs`
- `id` (Primary Key)
- `level` (DEBUG, INFO, WARNING, ERROR)
- `message` (Log message)
- `component` (System component)
- `source` (Source field)
- `created_at` (Log timestamp)
- `log_metadata` (Additional metadata JSON)

### ChromaDB Collections
- **Memory Collection**: Stores mission outcomes for learning
- **Context Collection**: Stores contextual information
- **Vector Search**: Semantic search capabilities

## 🔧 Database Management

### Connection Handling
```python
# Automatic database type detection
if DATABASE_URL.startswith("postgresql"):
    # PostgreSQL configuration
    engine = create_engine(DATABASE_URL)
else:
    # SQLite configuration (fallback)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
```

### Key Operations
- **Mission Creation**: Store new missions in PostgreSQL
- **Status Updates**: Real-time mission status tracking
- **Memory Storage**: Store outcomes in ChromaDB
- **Context Retrieval**: Search past experiences
- **System Logging**: Comprehensive event logging

## 🚀 Performance Characteristics

### PostgreSQL (Railway)
- **Scalability**: Cloud-hosted, auto-scaling
- **Reliability**: Managed service with backups
- **Performance**: Optimized for mission tracking
- **Connectivity**: Global access via Railway

### ChromaDB
- **Speed**: Local vector operations
- **Memory**: Efficient vector storage
- **Search**: Semantic similarity search
- **Learning**: Context-aware memory retrieval

## 📋 Configuration

### Environment Variables
```bash
DATABASE_URL=postgresql://postgres:LSvFcJSLjYBxsWrcTtgBUgLlLYBdPqiS@trolley.proxy.rlwy.net:44667/railway
VECTOR_DB_URL=http://localhost:8000
VECTOR_DB_TYPE=chromadb
CHROMA_PATH=db/chroma_memory
```

### Dependencies
```txt
sqlalchemy==2.0.30
psycopg2-binary==2.9.9
chromadb>=0.4.22,<0.5.0
```

## 🔍 Monitoring and Maintenance

### Health Checks
- Database connection validation
- ChromaDB availability checks
- Performance monitoring
- Error tracking and logging

### Backup Strategy
- **PostgreSQL**: Railway managed backups
- **ChromaDB**: Local file system backup
- **Configuration**: Version controlled settings

## 🎯 Benefits of Current Setup

### PostgreSQL (Railway)
- ✅ **Cloud-hosted**: No local database management
- ✅ **Scalable**: Auto-scaling with Railway
- ✅ **Reliable**: Managed service with backups
- ✅ **Global**: Accessible from anywhere
- ✅ **Production-ready**: Enterprise-grade database

### ChromaDB
- ✅ **Fast**: Local vector operations
- ✅ **Efficient**: Optimized for AI workloads
- ✅ **Flexible**: Easy to extend and customize
- ✅ **Learning**: Context-aware memory retrieval

### Combined Architecture
- ✅ **Best of Both**: Relational + Vector database
- ✅ **Optimized**: Each database for its purpose
- ✅ **Scalable**: Can handle growth
- ✅ **Reliable**: Redundant storage systems

## 📚 Related Documentation

- `CURRENT_VERSION_SUMMARY.md` - Complete system overview
- `SYSTEM_STATUS.md` - System capabilities and status
- `ARCHITECTURAL_PURITY_ACHIEVED.md` - Architecture details
- `STARTUP_GUIDE.md` - Setup and configuration

**The database architecture is optimized for the Sentient Supercharged Phoenix System's advanced cognitive processing capabilities.** 