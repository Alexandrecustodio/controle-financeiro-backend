# 🚀 Finance Manager - Guia Completo GitHub + Hospedagem

Este guia mostra como hospedar o Finance Manager no GitHub e fazer deploy em produção.

---

## 📋 Pré-requisitos

- Conta no GitHub
- Conta em um serviço de hospedagem (Heroku, Railway, Render, etc.)
- PostgreSQL (local ou em nuvem)
- Node.js 18+

---

## 🎯 Passo 1: Preparar Repositório GitHub

### 1.1 Criar Repositório

1. Acesse https://github.com/new
2. Nome: `finance-manager`
3. Descrição: "App de gestão financeira com React Native e Node.js"
4. Selecione **Public** (opcional)
5. Clique **Create repository**

### 1.2 Clonar e Fazer Push

```bash
# Clone o repositório vazio
git clone https://github.com/seu-usuario/finance-manager.git
cd finance-manager

# Copie os arquivos do projeto
cp -r /caminho/do/projeto/* .

# Faça commit inicial
git add .
git commit -m "Initial commit: Finance Manager app"
git push -u origin main
```

---

## 🗄️ Passo 2: Configurar Banco de Dados

### 2.1 Opção A: PostgreSQL Local (Desenvolvimento)

```bash
# Instale PostgreSQL
# macOS: brew install postgresql
# Windows: https://www.postgresql.org/download/windows/
# Linux: sudo apt-get install postgresql

# Crie banco de dados
createdb finance_manager

# Configure variáveis de ambiente
echo "DATABASE_URL=postgresql://user:password@localhost:5432/finance_manager" > .env.local
```

### 2.2 Opção B: PostgreSQL em Nuvem (Produção)

**Railway.app (Recomendado)**

1. Acesse https://railway.app
2. Clique "New Project"
3. Selecione "PostgreSQL"
4. Copie a `DATABASE_URL`
5. Adicione em `.env.production`

**Alternativas:**
- Heroku Postgres
- Render PostgreSQL
- AWS RDS

---

## 🔧 Passo 3: Configurar Variáveis de Ambiente

### 3.1 Criar `.env.local` (Desenvolvimento)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/finance_manager

# Server
PORT=3000
NODE_ENV=development

# Frontend
EXPO_PUBLIC_API_URL=http://localhost:3000/api

# Secrets (gere com: openssl rand -hex 32)
JWT_SECRET=seu_secret_aqui
SESSION_SECRET=seu_secret_aqui
```

### 3.2 Criar `.env.production` (Produção)

```env
# Database (do Railway/Render)
DATABASE_URL=postgresql://user:password@host:5432/finance_manager

# Server
PORT=3000
NODE_ENV=production

# Frontend
EXPO_PUBLIC_API_URL=https://seu-app.railway.app/api

# Secrets
JWT_SECRET=seu_secret_aqui
SESSION_SECRET=seu_secret_aqui
```

### 3.3 Adicionar ao `.gitignore`

```
.env.local
.env.production
.env.development
node_modules/
dist/
.expo/
```

---

## 📦 Passo 4: Estrutura do Projeto

```
finance-manager/
├── app/                    # Frontend React Native
│   ├── (tabs)/
│   ├── _layout.tsx
│   └── ...
├── server/                 # Backend Node.js
│   ├── _core/
│   ├── db.ts
│   ├── routers.ts
│   └── README.md
├── drizzle/                # Database schema
│   ├── schema.ts
│   └── migrations/
├── shared/                 # Código compartilhado
├── lib/                    # Utilitários
├── package.json
├── app.config.ts
├── .env.local
├── .env.production
├── .gitignore
├── README.md
└── DEPLOYMENT.md
```

---

## 🚀 Passo 5: Deploy no Railway

### 5.1 Conectar GitHub

1. Acesse https://railway.app
2. Clique "New Project"
3. Selecione "Deploy from GitHub"
4. Autorize Railway
5. Selecione `finance-manager`

### 5.2 Configurar Variáveis

1. No painel Railway, vá para "Variables"
2. Adicione:
   ```
   DATABASE_URL=postgresql://...
   NODE_ENV=production
   JWT_SECRET=seu_secret
   SESSION_SECRET=seu_secret
   EXPO_PUBLIC_API_URL=https://seu-app.railway.app/api
   ```

### 5.3 Deploy Automático

1. Cada push para `main` faz deploy automático
2. Monitore em https://railway.app/dashboard

---

## 📱 Passo 6: Conectar Frontend ao Backend

### 6.1 Atualizar `lib/trpc.ts`

```tsx
import { createTRPCReact } from "@trpc/react-query";
import type { AppRouter } from "../server/routers";

const API_URL = process.env.EXPO_PUBLIC_API_URL || "http://localhost:3000/api";

export const trpc = createTRPCReact<AppRouter>({
  config() {
    return {
      links: [
        httpBatchLink({
          url: `${API_URL}/trpc`,
          headers: {
            "Content-Type": "application/json",
          },
        }),
      ],
    };
  },
});
```

### 6.2 Usar API no Frontend

```tsx
import { trpc } from "@/lib/trpc";

function TransactionList() {
  const { data: transactions } = trpc.transactions.list.useQuery();
  
  return (
    <FlatList
      data={transactions}
      renderItem={({ item }) => <TransactionCard transaction={item} />}
    />
  );
}
```

---

## 🔐 Passo 7: Segurança

### 7.1 Secrets Seguros

```bash
# Gere secrets seguros
openssl rand -hex 32  # JWT_SECRET
openssl rand -hex 32  # SESSION_SECRET
```

### 7.2 HTTPS

- Railway fornece HTTPS automaticamente
- Configure CORS em `server/_core/index.ts`

### 7.3 Rate Limiting

```tsx
// server/routers.ts
import rateLimit from "express-rate-limit";

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
});

app.use(limiter);
```

---

## 📊 Passo 8: Monitoramento

### 8.1 Logs

```bash
# Ver logs no Railway
railway logs

# Ou no seu terminal
npm run dev
```

### 8.2 Métricas

- Railway Dashboard: https://railway.app/dashboard
- Monitore CPU, memória, requisições

---

## 🧪 Passo 9: Testes

### 9.1 Testar Localmente

```bash
# Terminal 1: Backend
npm run dev:server

# Terminal 2: Frontend
npm run dev:metro

# Escaneie QR code no Expo Go
```

### 9.2 Testar em Produção

```bash
# Build para produção
npm run build

# Teste o build
npm start
```

---

## 📋 Checklist de Deploy

- [ ] Repositório criado no GitHub
- [ ] Banco de dados configurado (PostgreSQL)
- [ ] Variáveis de ambiente definidas
- [ ] `.gitignore` configurado
- [ ] Railway conectado
- [ ] Deploy automático ativado
- [ ] Frontend conectado ao backend
- [ ] Testes passando
- [ ] HTTPS funcionando
- [ ] Logs monitorados

---

## 🆘 Troubleshooting

### "DATABASE_URL not found"
- Verifique `.env.production`
- Confirme que Railway está configurado

### "CORS error"
- Adicione frontend URL em CORS
- Verifique `server/_core/index.ts`

### "Build fails"
- Verifique `npm install`
- Confirme Node.js version

### "App não conecta ao backend"
- Verifique `EXPO_PUBLIC_API_URL`
- Teste com `curl` em produção

---

## 📚 Recursos

- [Railway Docs](https://docs.railway.app)
- [tRPC Docs](https://trpc.io)
- [Drizzle ORM](https://orm.drizzle.team)
- [React Native Docs](https://reactnative.dev)

---

**Seu app está pronto para produção! 🚀**
