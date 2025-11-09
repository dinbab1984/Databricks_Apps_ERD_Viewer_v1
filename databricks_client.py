"""
Databricks Unity Catalog Client
Handles connection and data retrieval from Databricks Unity Catalog
"""
import os
from typing import List, Dict, Optional, Mapping
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import TableInfo, ColumnInfo
from databricks.sdk.service.sql import StatementState
from databricks.sdk.core import Config

class DatabricksClient:
    def __init__(
        self,
        host: Optional[str] = None,
        token: Optional[str] = None,
        request_headers: Optional[Mapping[str, str]] = None,
        profile: Optional[str] = None,
    ):
        """
        Initialize Databricks WorkspaceClient.
        
        For Databricks Apps with User Authorization:
          - Extracts user token from X-Forwarded-Access-Token header
          - Creates client with auth_type="pat" for user identity
          
        For other environments:
          - Uses explicit token/host if provided
          - Falls back to environment variables or CLI profile

        Args:
          host: Optional workspace URL override.
          token: Optional access token override.
          request_headers: Optional HTTP headers (Databricks Apps - Streamlit st.context.headers).
          profile: Optional local CLI profile name.
        """
        # Determine workspace host
        workspace_host = host or os.getenv("DATABRICKS_HOST")
        
        # Normalize host URL
        if workspace_host and not workspace_host.startswith(('http://', 'https://')):
            workspace_host = f"https://{workspace_host}"
        
        # Extract user token from headers if running in Databricks Apps
        user_access_token = None
        user_email = None
        
        if request_headers:
            # Get user information from headers (Databricks Apps with User Authorization)
            user_access_token = request_headers.get("X-Forwarded-Access-Token")
            user_email = request_headers.get("X-Forwarded-Email")
            
            if user_access_token:
                print(f"✅ OBO: User token found in headers")
                print(f"✅ OBO: User email: {user_email}")
                print(f"✅ OBO: Token length: {len(user_access_token)}")
            else:
                print(f"⚠️  No X-Forwarded-Access-Token in headers")
        
        # Create WorkspaceClient following official pattern
        # Priority: explicit token > user token from headers > env vars/profile
        if token:
            # Explicit token provided
            print(f"Using explicit token parameter")
            self.client = WorkspaceClient(host=workspace_host, token=token, auth_type="pat")
            self._using_obo = False
            
        elif user_access_token:
            # User token from headers (Databricks Apps with User Authorization)
            # Following official example: WorkspaceClient(token=user_access_token, auth_type="pat")
            print(f"✅ Creating WorkspaceClient with user token (OBO mode)")
            print(f"✅ Using auth_type='pat' for user authentication")
            
            self.client = WorkspaceClient(
                host=workspace_host,
                token=user_access_token,
                auth_type="pat"  # Critical: treat user token as PAT
            )
            self._using_obo = True
            self._user_email = user_email
            
        else:
            # Fall back to environment variables or profile
            print(f"Using environment variables or profile for authentication")
            if profile:
                self.client = WorkspaceClient(host=workspace_host, profile=profile)
            else:
                self.client = WorkspaceClient(host=workspace_host)
            self._using_obo = False
        
        # Verify authentication
        if self._using_obo:
            print(f"✓ OBO Mode: ON")
            print(f"✓ User Email: {self._user_email}")
            print(f"✓ Auth Type: pat (Personal Access Token)")
        else:
            print(f"✓ OBO Mode: OFF")
            print(f"✓ Using: Environment variables or profile")
        print(f"{'='*60}\n")
        
        # Verify the authenticated identity
        try:
            current_user = self.client.current_user.me()
            print(f"🔐 AUTHENTICATED AS:")
            print(f"   Username: {current_user.user_name}")
            print(f"   Display Name: {getattr(current_user, 'display_name', 'N/A')}")
            print(f"   Active: {current_user.active}")
            
            # Check if it's a user or service principal
            import re
            uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
            is_sp = uuid_pattern.match(current_user.user_name) if current_user.user_name else False
            
            if is_sp:
                print(f"   Type: SERVICE PRINCIPAL ⚠️")
                if self._using_obo:
                    print(f"\n❌ ERROR: Expected user authentication but got Service Principal!")
                    print(f"   Check that User Authorization is enabled in app settings.")
            else:
                print(f"   Type: USER ✅")
                if self._using_obo:
                    print(f"\n✅ OBO WORKING: Running as {self._user_email}")
            
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"⚠️  Could not verify authenticated user: {e}")

    def list_catalogs(self) -> List[str]:
        """List all available catalogs"""
        try:
            print(f"DEBUG PERMISSIONS: Listing catalogs...")
            catalogs = list(self.client.catalogs.list())
            catalog_names = [catalog.name for catalog in catalogs if catalog.name]
            print(f"DEBUG PERMISSIONS: Found {len(catalog_names)} catalog(s): {catalog_names}")
            return catalog_names
        except Exception as e:
            print(f"ERROR: Failed to list catalogs: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def list_schemas(self, catalog_name: str) -> List[str]:
        """
        List all schemas in a catalog
        
        Args:
            catalog_name: Name of the catalog
        """
        try:
            print(f"\n{'='*60}")
            print(f"DEBUG PERMISSIONS: Listing schemas in catalog '{catalog_name}'...")
            print(f"DEBUG PERMISSIONS: Using OBO: {self._using_obo}")
            
            # Get current user for context
            try:
                current_user = self.client.current_user.me()
                emails = getattr(current_user, 'emails', None)
                if emails and len(emails) > 0:
                    email_obj = emails[0]
                    email_value = email_obj.value if hasattr(email_obj, 'value') else str(email_obj)
                    print(f"DEBUG PERMISSIONS: Current auth identity: {email_value}")
                    print(f"DEBUG PERMISSIONS: Auth user ID: {current_user.id}")
                    print(f"DEBUG PERMISSIONS: User name: {current_user.user_name}")
                    
                    # Check if it's actually a service principal
                    import re
                    uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
                    is_sp = (hasattr(current_user, 'application_id') and current_user.application_id) or \
                            (email_value and uuid_pattern.match(email_value))
                    
                    print(f"DEBUG PERMISSIONS: Identity type: {'SERVICE_PRINCIPAL' if is_sp else 'USER'}")
            except Exception as e:
                print(f"DEBUG PERMISSIONS: Could not get user info: {e}")
            
            # Verify which principal Unity Catalog sees
            try:
                warehouse_id = self._get_warehouse_id()
                if warehouse_id:
                    print(f"DEBUG PERMISSIONS: Querying UC to verify effective principal...")
                    uc_identity_query = "SELECT current_user() as current_user"
                    result = self._execute_sql_query(uc_identity_query)
                    if result and len(result) > 0:
                        uc_user = result[0].get('current_user', 'Unknown')
                        print(f"DEBUG PERMISSIONS: Unity Catalog sees principal: {uc_user}")
                        print(f"DEBUG PERMISSIONS: (If this is a UUID, UC is using SP despite OBO token)")
                    else:
                        print(f"DEBUG PERMISSIONS: Could not determine UC principal")
            except Exception as e:
                print(f"DEBUG PERMISSIONS: Error checking UC principal: {e}")
            
            # List schemas
            schemas = list(self.client.schemas.list(catalog_name=catalog_name))
            print(f"DEBUG PERMISSIONS: SDK returned {len(schemas)} schema object(s)")
            
            # Debug each schema
            for i, schema in enumerate(schemas[:10]):  # Show first 10 for debugging
                print(f"  Schema {i+1}: {schema.name} (owner: {getattr(schema, 'owner', 'N/A')})")
            
            schema_names = [schema.name for schema in schemas if schema.name]
            print(f"DEBUG PERMISSIONS: After filtering: {len(schema_names)} schema(s)")
            print(f"DEBUG PERMISSIONS: Schema names: {schema_names}")
            
            if len(schemas) != len(schema_names):
                print(f"DEBUG PERMISSIONS: ⚠️ Some schemas filtered out (had null names)")
            
            if not schema_names:
                print(f"\nDEBUG PERMISSIONS: ⚠️ No schemas found. Checking permissions...")
                print(f"DEBUG PERMISSIONS: Run this query in SQL to see what you should have access to:")
                print(f"  SHOW SCHEMAS IN {catalog_name};")
                print(f"\nDEBUG PERMISSIONS: Possible reasons:")
                print(f"  1. User doesn't have USE CATALOG permission on '{catalog_name}'")
                print(f"  2. User doesn't have USE SCHEMA on any schemas")
                print(f"  3. Catalog '{catalog_name}' is empty")
                print(f"  4. SDK list API has different behavior than SHOW SCHEMAS")
            
            print(f"{'='*60}\n")
            return schema_names
            
        except Exception as e:
            print(f"\nERROR: Failed to list schemas for catalog '{catalog_name}': {e}")
            print(f"DEBUG PERMISSIONS: This often means insufficient permissions.")
            print(f"DEBUG PERMISSIONS: Required: USE CATALOG on '{catalog_name}' + USE SCHEMA permissions")
            print(f"\nDEBUG PERMISSIONS: Try running this in SQL to verify:")
            print(f"  SHOW GRANTS ON CATALOG {catalog_name};")
            print(f"  SHOW SCHEMAS IN {catalog_name};")
            import traceback
            traceback.print_exc()
            return []
    
    def list_tables(self, catalog_name: str, schema_name: str) -> List[str]:
        """
        List all tables in a schema
        
        Args:
            catalog_name: Name of the catalog
            schema_name: Name of the schema
        """
        try:
            print(f"DEBUG PERMISSIONS: Listing tables in '{catalog_name}.{schema_name}'...")
            tables = list(self.client.tables.list(
                catalog_name=catalog_name,
                schema_name=schema_name
            ))
            table_names = [table.name for table in tables if table.name]
            print(f"DEBUG PERMISSIONS: Found {len(table_names)} table(s) in '{catalog_name}.{schema_name}'")
            
            if not table_names:
                print(f"DEBUG PERMISSIONS: ⚠️ No tables found. Possible reasons:")
                print(f"DEBUG PERMISSIONS:   - User doesn't have SELECT permission on tables in this schema")
                print(f"DEBUG PERMISSIONS:   - Schema '{schema_name}' is empty")
            
            return table_names
        except Exception as e:
            print(f"ERROR: Failed to list tables for {catalog_name}.{schema_name}: {e}")
            print(f"DEBUG PERMISSIONS: Required: SELECT permission on tables in schema")
            import traceback
            traceback.print_exc()
            return []
    
    def _get_warehouse_id(self) -> Optional[str]:
        """Get the first available SQL warehouse ID"""
        try:
            if not hasattr(self, '_cached_warehouse_id'):
                warehouses = list(self.client.warehouses.list())
                if warehouses and len(warehouses) > 0:
                    self._cached_warehouse_id = warehouses[0].id
                    print(f"DEBUG: Using SQL warehouse: {self._cached_warehouse_id}")
                else:
                    print("DEBUG: No SQL warehouses found")
                    self._cached_warehouse_id = None
            return self._cached_warehouse_id
        except Exception as e:
            print(f"DEBUG: Error getting warehouse: {e}")
            return None
    
    def _execute_sql_query(self, query: str) -> List[Dict]:
        """
        Execute a SQL query and return results
        
        Args:
            query: SQL query to execute
            
        Returns:
            List of result rows as dictionaries
        """
        try:
            warehouse_id = self._get_warehouse_id()
            if not warehouse_id:
                print("DEBUG SQL: No warehouse available, skipping SQL query")
                return []
            
            print(f"DEBUG SQL: Executing query (first 100 chars):\n{query[:100]}...")
            statement = self.client.statement_execution.execute_statement(
                warehouse_id=warehouse_id,
                statement=query,
                wait_timeout="30s"
            )
            
            if statement.status and statement.status.state == StatementState.SUCCEEDED:
                if statement.result and statement.result.data_array:
                    # Get column names
                    columns = [col.name for col in (statement.manifest.schema.columns or [])]
                    
                    # Convert to list of dicts
                    results = []
                    for row in statement.result.data_array:
                        row_dict = {columns[i]: row[i] for i in range(len(columns))}
                        results.append(row_dict)
                    
                    print(f"DEBUG SQL: Got {len(results)} result(s)")
                    return results
                else:
                    print("DEBUG SQL: No results returned")
                    return []
            else:
                print(f"DEBUG SQL: Query failed with state: {statement.status.state if statement.status else 'unknown'}")
                return []
                
        except Exception as e:
            print(f"DEBUG SQL: Error executing query: {e}")
            return []
    
    def _get_all_schema_constraints_bulk(self, catalog_name: str, schema_name: str) -> Dict[str, tuple]:
        """
        Get ALL constraints for ALL tables in a schema using bulk queries (much faster!)
        
        Returns:
            Dictionary mapping table_name -> (primary_keys, foreign_keys)
        """
        constraints_by_table = {}
        
        try:
            print(f"\nDEBUG: Fetching ALL constraints for schema {catalog_name}.{schema_name} in bulk...")
            
            # Single query to get ALL constraints for the entire schema
            all_constraints_query = f"""
            SELECT 
                table_name,
                constraint_name,
                constraint_type
            FROM {catalog_name}.information_schema.table_constraints
            WHERE table_catalog = '{catalog_name}'
              AND table_schema = '{schema_name}'
            """
            
            all_constraints = self._execute_sql_query(all_constraints_query)
            print(f"DEBUG: Found {len(all_constraints)} total constraint(s) across all tables")
            
            # Single query to get ALL primary key columns for the entire schema
            all_pk_query = f"""
            SELECT 
                kcu.table_name,
                kcu.column_name,
                kcu.constraint_name
            FROM {catalog_name}.information_schema.key_column_usage kcu
            JOIN {catalog_name}.information_schema.table_constraints tc
                ON kcu.constraint_name = tc.constraint_name
                AND kcu.table_catalog = tc.table_catalog
                AND kcu.table_schema = tc.table_schema
                AND kcu.table_name = tc.table_name
            WHERE tc.table_catalog = '{catalog_name}'
              AND tc.table_schema = '{schema_name}'
              AND tc.constraint_type = 'PRIMARY KEY'
            ORDER BY kcu.table_name, kcu.ordinal_position
            """
            
            all_pk_columns = self._execute_sql_query(all_pk_query)
            print(f"DEBUG: Found {len(all_pk_columns)} primary key column(s) across all tables")
            
            # Single query to get ALL foreign key relationships for the entire schema
            all_fk_query = f"""
            SELECT 
                kcu.table_name,
                kcu.column_name as child_column,
                kcu.constraint_name,
                rc.unique_constraint_catalog as parent_catalog,
                rc.unique_constraint_schema as parent_schema,
                kcu2.table_name as parent_table,
                kcu2.column_name as parent_column
            FROM {catalog_name}.information_schema.key_column_usage kcu
            JOIN {catalog_name}.information_schema.referential_constraints rc
                ON kcu.constraint_name = rc.constraint_name
                AND kcu.table_catalog = rc.constraint_catalog
                AND kcu.table_schema = rc.constraint_schema
            JOIN {catalog_name}.information_schema.key_column_usage kcu2
                ON rc.unique_constraint_name = kcu2.constraint_name
                AND rc.unique_constraint_catalog = kcu2.table_catalog
                AND rc.unique_constraint_schema = kcu2.table_schema
            WHERE kcu.table_catalog = '{catalog_name}'
              AND kcu.table_schema = '{schema_name}'
            ORDER BY kcu.table_name, kcu.constraint_name, kcu.ordinal_position
            """
            
            all_fk_rows = self._execute_sql_query(all_fk_query)
            print(f"DEBUG: Found {len(all_fk_rows)} foreign key column(s) across all tables")
            
            # Organize PK columns by table
            pk_by_table = {}
            for row in all_pk_columns:
                table = row['table_name']
                if table not in pk_by_table:
                    pk_by_table[table] = []
                pk_by_table[table].append(row['column_name'])
            
            # Organize FK relationships by table and constraint
            fk_by_table = {}
            for row in all_fk_rows:
                table = row['table_name']
                constraint = row['constraint_name']
                
                if table not in fk_by_table:
                    fk_by_table[table] = {}
                
                if constraint not in fk_by_table[table]:
                    fk_by_table[table][constraint] = {
                        'child_columns': [],
                        'parent_table': f"{row['parent_catalog']}.{row['parent_schema']}.{row['parent_table']}",
                        'parent_columns': [],
                        'name': constraint
                    }
                
                fk_by_table[table][constraint]['child_columns'].append(row['child_column'])
                fk_by_table[table][constraint]['parent_columns'].append(row['parent_column'])
            
            # Build final result for each table
            all_table_names = set()
            for constraint in all_constraints:
                all_table_names.add(constraint['table_name'])
            
            for table_name in all_table_names:
                primary_keys = pk_by_table.get(table_name, [])
                foreign_keys = list(fk_by_table.get(table_name, {}).values())
                
                constraints_by_table[table_name] = (primary_keys, foreign_keys)
                
                if primary_keys or foreign_keys:
                    print(f"DEBUG: {table_name}: {len(primary_keys)} PK(s), {len(foreign_keys)} FK(s)")
            
            print(f"DEBUG: Bulk constraint fetch complete for {len(constraints_by_table)} table(s)")
            
        except Exception as e:
            print(f"DEBUG: Error in bulk constraint fetch: {e}")
        
        return constraints_by_table
    
    def get_table_info(self, catalog_name: str, schema_name: str, table_name: str) -> Optional[Dict]:
        """
        Get detailed information about a table including columns
        Note: For bulk operations, use get_schema_metadata() which is much faster
        
        Args:
            catalog_name: Name of the catalog
            schema_name: Name of the schema
            table_name: Name of the table
        """
        try:
            full_name = f"{catalog_name}.{schema_name}.{table_name}"
            table = self.client.tables.get(full_name=full_name)
            
            columns_info = []
            if table.columns:
                for col in table.columns:
                    columns_info.append({
                        'name': col.name,
                        'type': col.type_name.value if col.type_name else 'unknown',
                        'nullable': col.nullable if col.nullable is not None else True,
                        'comment': col.comment or ''
                    })
            
            # Note: Constraints not fetched here for performance
            # Use get_schema_metadata() for bulk constraint fetching
            
            return {
                'name': table_name,
                'full_name': full_name,
                'columns': columns_info,
                'primary_keys': [],
                'foreign_keys': [],
                'comment': table.comment or '',
                'table_type': table.table_type.value if table.table_type else 'TABLE'
            }
        except Exception as e:
            print(f"Error getting table info for {catalog_name}.{schema_name}.{table_name}: {e}")
            return None
    
    def get_schema_metadata(self, catalog_name: str, schema_name: str) -> Dict[str, Dict]:
        """
        Get metadata for all tables in a schema (optimized with bulk constraint fetching)
        
        Args:
            catalog_name: Name of the catalog
            schema_name: Name of the schema
            
        Returns:
            Dictionary mapping table names to their metadata
        """
        tables = self.list_tables(catalog_name, schema_name)
        schema_metadata = {}
        
        # BULK FETCH: Get ALL constraints for ALL tables at once (much faster!)
        print(f"\n🚀 PERFORMANCE OPTIMIZATION: Fetching constraints in bulk for all {len(tables)} tables...")
        all_constraints = self._get_all_schema_constraints_bulk(catalog_name, schema_name)
        print(f"✅ Bulk constraint fetch complete!\n")
        
        for table_name in tables:
            try:
                full_name = f"{catalog_name}.{schema_name}.{table_name}"
                table = self.client.tables.get(full_name=full_name)
                
                columns_info = []
                if table.columns:
                    for col in table.columns:
                        columns_info.append({
                            'name': col.name,
                            'type': col.type_name.value if col.type_name else 'unknown',
                            'nullable': col.nullable if col.nullable is not None else True,
                            'comment': col.comment or ''
                        })
                
                # Get constraints from bulk fetch (no SQL queries per table!)
                primary_keys, foreign_keys = all_constraints.get(table_name, ([], []))
                
                schema_metadata[table_name] = {
                    'name': table_name,
                    'full_name': full_name,
                    'columns': columns_info,
                    'primary_keys': primary_keys,
                    'foreign_keys': foreign_keys,
                    'comment': table.comment or '',
                    'table_type': table.table_type.value if table.table_type else 'TABLE'
                }
                
            except Exception as e:
                print(f"Error getting table info for {catalog_name}.{schema_name}.{table_name}: {e}")
        
        return schema_metadata

